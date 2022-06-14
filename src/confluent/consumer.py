from confluent_kafka import Consumer
from dotenv import load_dotenv
import os

load_dotenv() 


consumer = Consumer({
    'bootstrap.servers': os.getenv("CONFLUENT_BOOTSTRAP_SERVER"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("CONFLUENT_SASL_USERNAME"),
    'sasl.password': os.getenv("CONFLUENT_SASL_PASSWORD"),

    'group.id': 'group-x',
    'auto.offset.reset': 'earliest',
    'session.timeout.ms': 45000
})

consumer.subscribe(['transactions'])

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))

c.close()