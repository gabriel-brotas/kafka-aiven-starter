from kafka import KafkaConsumer
from dotenv import load_dotenv
import os

load_dotenv()

consumer = KafkaConsumer(
    "transactions",
    # bootstrap_servers="kafka-aiven_kafka_1:9092" # dev,
    group_id="aiven-consumer-py",

    # prod
    bootstrap_servers=os.getenv("AIVEN_BOOTSTRAP_SERVER"), #prod 
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username=os.getenv("AIVEN_SASL_USERNAME"),
    sasl_plain_password=os.getenv("AIVEN_SASL_PASSWORD"),
    ssl_cafile="ca.pem"
)

print("Consumer running")
for msg in consumer:
    print (msg)

