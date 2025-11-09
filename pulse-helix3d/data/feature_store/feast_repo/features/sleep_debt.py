from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32

from data.feature_store.feast_repo.entities import user

sleep_debt = FeatureView(
    name="sleep_debt",
    entities=[user],
    ttl=timedelta(days=14),
    schema=[Field(name="sleep_debt_hours", dtype=Float32)],
    online=True,
    source=None,
)
