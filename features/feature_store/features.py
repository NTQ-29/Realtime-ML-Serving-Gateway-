# features/feature_store/features.py
from datetime import timedelta
from feast import Entity, Field, FeatureView, ValueType, Field
from feast.types import Float32, Int64

# Define the primary key entity
user_entity = Entity(name="user_id", value_type=ValueType.STRING, description="The unique user identifier")

# 1. Batch Feature View (Updated nightly via ETL into S3)
user_batch_features = FeatureView(
    name="user_batch_features",
    entities=[user_entity],
    ttl=timedelta(days=90),
    schema=[
        Field(name="customer_lifetime_value", dtype=Float32),
        Field(name="historical_conversion_rate", dtype=Float32),
    ],
    online=True,
    source=None # In production, points to an S3/Parquet source
)

# 2. Stream Feature View (Updated continuously via Kafka)
user_stream_features = FeatureView(
    name="user_stream_features",
    entities=[user_entity],
    ttl=timedelta(days=1),
    schema=[
        Field(name="session_click_count_30s", dtype=Int64),
    ],
    online=True,
    source=None # In production, points to a Kafka/Push source
)
