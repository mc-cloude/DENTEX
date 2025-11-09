from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32

from data.feature_store.feast_repo.entities import user

strain_rollavg = FeatureView(
    name="strain_rollavg",
    entities=[user],
    ttl=timedelta(days=7),
    schema=[Field(name="strain_7d_avg", dtype=Float32)],
    online=True,
    source=None,
)
