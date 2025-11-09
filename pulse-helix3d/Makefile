.PHONY: contract.check dq.check test backend.run frontend.web terraform.apply helm.sync

contract.check:
python data/contracts/validate_contract.py --src $(SRC) --schema $(SCHEMA)

dq.check:
pytest data/retention/dsr/tests -q

test:
pytest tests -q

backend.run:
uvicorn backend.services.api_gateway.main:app --reload

frontend.web:
flutter build web --source-dir frontend

terraform.apply:
cd terraform/environments/prod && terraform init && terraform apply -auto-approve

helm.sync:
cd ops/helmfile && helmfile -f helmfile-envs.yaml sync
