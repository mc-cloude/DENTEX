from __future__ import annotations

import asyncio

from data.retention.dsr.orchestrator import execute


def test_execute_dsr_event_loop():
    result = asyncio.run(execute("job-1", "user-1"))
    assert result.redis_purged
    assert result.weaviate_deleted
    assert result.audit_appended
