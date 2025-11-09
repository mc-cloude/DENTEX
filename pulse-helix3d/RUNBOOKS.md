# Pulse HELIX3D Runbooks

## DSR Execution
1. Trigger `/dsr/erase` via API Gateway.
2. Monitor job status in `/dsr/status/{job_id}`; expected completion < 5 minutes.
3. Validate Redis, Feast online, Weaviate deletions via orchestrator logs.
4. Append audit reference to ICP consent canister.

## Restore Drill
1. Retrieve latest Marquez lineage backup from S3 `pulse-prod-lineage`.
2. Restore Postgres snapshots; target RTO ≤ 4h, RPO ≤ 24h.
3. Run Helmfile sync to redeploy runtime and data planes.
4. Execute smoke tests `pytest tests/smoke -q`.

## Key Rotation
1. Update External Secrets Operator references using Terraform module `eso_secret`.
2. Rotate KMS-backed secrets for Redis, Weaviate, and OIDC credentials.
3. Verify reload via `/healthz` and Prometheus metrics.

## Incident Response
1. Inspect OPA decisions using `/metrics` and OPA logs for deny events.
2. If guardian flags unsafe output, escalate to compliance guard and annotate Marquez lineage.
3. Use Helm rollback to revert failing releases if p95 latency exceeds SLO.

## Region Failover
1. Apply Terraform in staging to ensure parity.
2. Promote staging images to production with `.github/workflows/promotion.yml`.
3. Update DNS records for `ai.pulse.gcc` and `lineage.pulse.gcc` to staging ingress.
4. Communicate via Slack `#pulse-alerts`.
