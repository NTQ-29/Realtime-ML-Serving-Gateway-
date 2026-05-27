# features/streaming/consumer.py
import json
from kafka import KafkaConsumer
from feast import FeatureStore

def start_feature_stream_processor():
    # Initialize Feast store connection
    store = FeatureStore(repo_path="./features/feature_store")
    
    # Connect to Kafka topic ingestion pipeline
    consumer = KafkaConsumer(
        "user-activity-events",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    
    print("🚀 Real-time feature streaming worker started. Listening to Kafka...")
    
    for message in consumer:
        event_data = message.value
        user_id = event_data["user_id"]
        clicks_in_window = event_data["clicks_30s"]
        
        # Format feature records for explicit push injection into Redis online store
        feature_updates = {
            "session_click_count_30s": [clicks_in_window]
        }
        
        # Instantly push to Redis
        store.push(
            feature_view_name="user_stream_features",
            event_df=[{"user_id": user_id, **feature_updates}]
        )
        print(f"[STREAM UPDATE] Syncing features for {user_id} -> Clicks: {clicks_in_window}")

if __name__ == "__main__":
    # Kept ready for deployment structure execution
    pass
