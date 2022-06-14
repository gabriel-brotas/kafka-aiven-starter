from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from dotenv import load_dotenv
import os

load_dotenv() 

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
      print('Message delivery failed: {}'.format(err))
    else:
      print('Message delivered to {} on partition [{}]'.format(msg.topic(), msg.partition())) #NOSONAR

value_schema = avro.load("./src/confluent/order.avsc")

avroProducer = AvroProducer({
    'bootstrap.servers': os.getenv("CONFLUENT_BOOTSTRAP_SERVER"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("CONFLUENT_SASL_USERNAME"),
    'sasl.password': os.getenv("CONFLUENT_SASL_PASSWORD"),
    'schema.registry.url': os.getenv("CONFLUENT_SCHEMA_REGISTRY_URL"),
    'schema.registry.basic.auth.credentials.source': 'USER_INFO',
    'schema.registry.basic.auth.user.info': '{}'.format(os.getenv("CONFLUENT_SCHEMA_REGISTRY_AUTH_USER_INFO")),

    'on_delivery': delivery_report,
}, default_value_schema=value_schema)

transactions = [
    {'orderId': 1, 'orderTime': 1607641868, "orderAddress": "Gleba E, street 14"},
    {'orderId': 2, 'orderTime': 1607641869, "orderAddress": "Gleba E, st 14"},
    {'orderId': 3, 'orderTime': 1607641870, "orderAddress": "Maine, str 14"},
]

for data in transactions:
    avroProducer.produce(topic='orders', value=data)


avroProducer.flush()
