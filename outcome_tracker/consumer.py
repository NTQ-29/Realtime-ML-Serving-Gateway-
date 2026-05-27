# outcome_tracker/consumer.py
import json
import requests
from kafka import KafkaConsumer

GATEWAY_REWARD_URL = "http://localhost:8000/reward"

def start_outcome_consumer():
    """
    Listens to business conversion events and updates the Thompson Sampling states.
    """
    consumer = KafkaConsumer(
        "model-conversion-outcomes",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    
    print("📥 Delayed Reward Outcome Tracker active. Monitoring business conversions...")
    
    for message in consumer:
        outcome_event = message.value
        prediction_id = outcome_event["prediction_id"]
        served_by_model = outcome_event["served_by_model"]
        converted = outcome_event["converted"] # boolean success metric
        
        # Post the feedback back to the Gateway Router API to update Alpha/Beta parameters
        payload = {
            "prediction_id": prediction_id,
            "model_id": served_by_model,
            "success": converted
        }
        
        try:
            response = requests.post(GATEWAY_REWARD_URL, params=payload)
            if response.status_code == 200:
                print(f"[REWARD SYNC] Successfully updated Bandit parameters for model: {served_by_model}")
            else:
                print(f"[WARNING] Failed to sync reward state for {prediction_id}")
        except Exception as e:
            print(f"[ERROR] Communication breakdown with serving gateway: {str(e)}")

if __name__ == "__main__":
    # Kept ready for deployment structure execution
    pass
