import os
import json
from pathlib import Path

import argparse
import numpy as np
import SimpleITK as sitk

from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog

from hierarchialdet import DiffusionDetDatasetMapper, add_diffusiondet_config, DiffusionDetWithTTA
from hierarchialdet.util.model_ema import add_model_ema_configs, may_build_model_ema, may_get_ema_checkpointer, EMAHook, \
    apply_model_ema_and_restore, EMADetectionCheckpointer
from hierarchialdet.predictor import VisualizationDemo

def custom_format_output(outputs, img_ids):
    boxes = []
    for index, instances in enumerate(outputs):
        if not len(instances):
            continue

        scores = getattr(instances, "scores", None)
        pred_boxes = instances.pred_boxes.tensor.cpu().numpy()
        cls1 = getattr(instances, "pred_classes_1", None)
        cls2 = getattr(instances, "pred_classes_2", None)
        cls3 = getattr(instances, "pred_classes_3", None)

        for i in range(len(instances)):
            bbox_coords = pred_boxes[i].tolist()
            img_id = img_ids[index]

            box = {
                "name": f"{int(cls1[i]) if cls1 is not None else -1} - "
                        f"{int(cls2[i]) if cls2 is not None else -1} - "
                        f"{int(cls3[i]) if cls3 is not None else -1}",
                "corners": [
                    [bbox_coords[0], bbox_coords[1], img_id],
                    [bbox_coords[0], bbox_coords[3], img_id],
                    [bbox_coords[2], bbox_coords[1], img_id],
                    [bbox_coords[2], bbox_coords[3], img_id],
                ],
                "probability": float(scores[i].item()) if scores is not None else 0.0,
            }
            boxes.append(box)

    return {
        "name": "Regions of interest",
        "type": "Multiple 2D bounding boxes",
        "boxes": boxes,
        "version": {"major": 1, "minor": 0},
    }


def coco_format_output(outputs, img_ids):
    coco_annotations = []
    for index, instances in enumerate(outputs):
        if not len(instances):
            continue

        scores = getattr(instances, "scores", None)
        pred_boxes = instances.pred_boxes.tensor.cpu().numpy()
        cls1 = getattr(instances, "pred_classes_1", None)
        cls2 = getattr(instances, "pred_classes_2", None)
        cls3 = getattr(instances, "pred_classes_3", None)

        for i in range(len(instances)):
            bbox = pred_boxes[i].tolist()
            bbox[2] = bbox[2] - bbox[0]
            bbox[3] = bbox[3] - bbox[1]

            coco_annotations.append(
                {
                    "image_id": img_ids[index],
                    "category_id_1": int(cls1[i]) if cls1 is not None else -1,
                    "category_id_2": int(cls2[i]) if cls2 is not None else -1,
                    "category_id_3": int(cls3[i]) if cls3 is not None else -1,
                    "bbox": bbox,
                    "score": float(scores[i].item()) if scores is not None else 0.0,
                }
            )
    return coco_annotations


def get_parser():
    parser = argparse.ArgumentParser(description="Detectron2 demo for builtin configs")


    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.0,
        help="Minimum score for instance predictions to be shown",
    )

    parser.add_argument(
        "--config-file",
        type=str,
        default=None,
        help="Path to the model config file. Overrides PULSE_CONFIG_PATH if provided.",
    )

    parser.add_argument(
        "--model-weights",
        type=str,
        default=None,
        help="Path to the trained weights file. Overrides PULSE_WEIGHTS_PATH if provided.",
    )

    parser.add_argument(
        "--input-volume",
        type=str,
        default=None,
        help="Path to the input .mha volume. Overrides PULSE_INPUT_VOLUME if provided.",
    )

    parser.add_argument(
        "--input-dir",
        type=str,
        default=None,
        help="Directory to search for .mha volumes when --input-volume is not supplied.",
    )

    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Destination file for inference results in JSON format.",
    )

    parser.add_argument(
        "--nclass",
        type=int,
        default=3,
        help="Number of trained classes",
    )

    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=[],
        nargs=argparse.REMAINDER,
    )
    return parser


class Hierarchialdet:
    def __init__(self):
        self.cfg = None
        self.demo = None
        self.args = None
        self.image_lookup = {}
        self.image_sequence = []

    def _coerce_args(self, args):
        if args is None:
            return get_parser().parse_args()
        if isinstance(args, argparse.Namespace):
            return args
        if isinstance(args, dict):
            return argparse.Namespace(**args)
        raise TypeError(f"Unsupported args type: {type(args)!r}")

    def setup(self, args=None):
        args = self._coerce_args(args)
        self.args = args
        self.cfg = get_cfg()
        add_diffusiondet_config(self.cfg)
        add_model_ema_configs(self.cfg)

        base_dir = Path(__file__).resolve().parent
        default_config = base_dir / "configs/diffdet.custom.swinbase.nonpretrain.yaml"
        config_override = args.config_file or os.environ.get("PULSE_CONFIG_PATH")
        config_path = Path(config_override) if config_override else default_config
        if not config_path.is_absolute():
            config_path = (base_dir / config_path).resolve()
        self.cfg.merge_from_file(str(config_path))

        weights_override = args.model_weights or os.environ.get("PULSE_WEIGHTS_PATH")
        if weights_override:
            weights_path = Path(weights_override)
            if not weights_path.is_absolute():
                weights_path = (base_dir / weights_path).resolve()
            self.cfg.MODEL.WEIGHTS = str(weights_path)
        else:
            default_weights = base_dir / "pretrained_model/model_final.pth"
            if default_weights.exists():
                self.cfg.MODEL.WEIGHTS = str(default_weights)

        self.cfg.merge_from_list(args.opts)
        self.cfg.MODEL.RETINANET.SCORE_THRESH_TEST = args.confidence_threshold
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = args.confidence_threshold
        self.cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = args.confidence_threshold
        self.cfg.freeze()
        self.demo = VisualizationDemo(self.cfg)

        dataset_name = self.cfg.DATASETS.TEST[0] if len(self.cfg.DATASETS.TEST) else None
        self.image_lookup = {}
        self.image_sequence = []
        if dataset_name:
            metadata = MetadataCatalog.get(dataset_name)
            json_file = getattr(metadata, "json_file", None)
            if json_file and os.path.isfile(json_file):
                with open(json_file, "r") as dataset_file:
                    dataset = json.load(dataset_file)
                images = dataset.get("images", [])
                self.image_sequence = [img["file_name"] for img in sorted(images, key=lambda x: x.get("id", 0))]
                self.image_lookup = {img["file_name"]: img["id"] for img in images}

    def _resolve_image_name(self, index: int) -> str:
        if index < len(self.image_sequence):
            return self.image_sequence[index]

        fallback = f"val_{index}.png"
        if fallback in self.image_lookup:
            return fallback
        return f"slice_{index}.png"

    def _extract_slices(self, volume_array):
        array = np.asarray(volume_array)
        if array.ndim == 2:
            return [array]
        if array.ndim == 3:
            return [array[idx] for idx in range(array.shape[0])]
        if array.ndim == 4:
            return [array[idx] for idx in range(array.shape[0])]
        raise ValueError(f"Unsupported volume shape: {array.shape}")

    def _prepare_slice(self, slice_array):
        image = np.asarray(slice_array)
        if image.ndim == 3 and image.shape[0] in (1, 3) and image.shape[-1] not in (1, 3):
            image = np.moveaxis(image, 0, -1)
        if image.ndim == 2:
            image = np.stack([image] * 3, axis=-1)
        if image.ndim == 3 and image.shape[-1] == 1:
            image = np.repeat(image, 3, axis=-1)
        if image.ndim != 3:
            raise ValueError(f"Unexpected slice shape {image.shape}")

        if image.dtype != np.uint8:
            min_val = float(image.min())
            max_val = float(image.max())
            if max_val > min_val:
                image = (image - min_val) / (max_val - min_val)
            image = (np.clip(image, 0.0, 1.0) * 255).astype(np.uint8)

        return image

    def process(self, args=None):
        if args is not None or self.demo is None or self.args is None:
            self.setup(args)
        args = self.args

        all_outputs = []
        img_ids = []

        input_dir = args.input_dir or os.environ.get("PULSE_INPUT_DIR", "/input/images/panoramic-dental-xrays")
        input_dir_path = Path(input_dir).resolve()
        volume_override = args.input_volume or os.environ.get("PULSE_INPUT_VOLUME")

        if volume_override:
            volume_path = Path(volume_override)
            if not volume_path.is_absolute():
                volume_path = (input_dir_path / volume_path).resolve()
        else:
            candidates = sorted(input_dir_path.glob("*.mha"))
            if not candidates:
                raise FileNotFoundError(f"No .mha volumes found in {input_dir_path}")
            volume_path = candidates[0]

        if not volume_path.exists():
            raise FileNotFoundError(f"Input volume not found at {volume_path}")

        image = sitk.ReadImage(str(volume_path))
        image_array = sitk.GetArrayFromImage(image)
        slices = self._extract_slices(image_array)

        for idx, slice_array in enumerate(slices):
            prepared_slice = self._prepare_slice(slice_array)
            predictions, _ = self.demo.run_on_image(prepared_slice)
            instances = predictions.get("instances")
            if instances is None:
                instances = []
            all_outputs.append(instances)

            image_name = self._resolve_image_name(idx)
            img_ids.append(self.image_lookup.get(image_name, idx + 1))

        coco_annotations = custom_format_output(all_outputs, img_ids)

        output_override = args.output_file or os.environ.get(
            "PULSE_OUTPUT_FILE", "/output/abnormal-teeth-detection.json"
        )
        output_path = Path(output_override)
        if not output_path.is_absolute():
            output_path = (Path.cwd() / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w") as f:
            json.dump(coco_annotations, f)

        print(f"Inference completed. Results saved to {output_path}")


if __name__ == "__main__":
    Hierarchialdet().process()
