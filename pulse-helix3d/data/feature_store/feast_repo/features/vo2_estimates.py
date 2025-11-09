from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32

from data.feature_store.feast_repo.entities import user

vo2_estimates = FeatureView(
    name="vo2_estimates",
    entities=[user],
    ttl=timedelta(days=30),
    schema=[Field(name="vo2_max", dtype=Float32)],
    online=True,
    source=None,
)
