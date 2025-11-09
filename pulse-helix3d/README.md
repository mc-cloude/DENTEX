# Pulse HELIX3D — CrewAI Edition (v1.0.0-RC3)

Pulse HELIX3D delivers a GCC-first, HIPAA/GDPR-aligned employee vitality
platform with AI-assisted planning, nutrition and clinical insights, and
tight data governance.

## Repository Layout

Refer to the directories for backend FastAPI services, Rust ICP canisters,
CrewAI configuration, Flutter frontend, data contracts, infrastructure, and
automation. Each subsystem is self-documented with README snippets and
configuration files.

## Getting Started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # optional if created
uvicorn backend.services.api_gateway.main:app --reload
```

Run Flutter web build:

```bash
flutter build web --source-dir frontend
```

Validate data contracts and run smoke tests:

```bash
make contract.check SRC=data/contracts/examples/fitbit_daily_sample.json SCHEMA=data/contracts/wearables/v1/fitbit_daily.json
make test
```

Terraform deployment (prod):

```bash
make terraform.apply
```

Helmfile sync:

```bash
make helm.sync
```

## Release Artifacts

Tagged releases publish `pulse_helix3d_rc3_full.zip` containing contracts,
DQ suites, lineage specifications, and documentation for external audit.
