from confluent_kafka import Producer
import json
from dotenv import load_dotenv
import os

load_dotenv() 

producer = Producer({
  'bootstrap.servers': os.getenv("CONFLUENT_BOOTSTRAP_SERVER"),
  'security.protocol': 'SASL_SSL',
  'sasl.mechanisms': 'PLAIN',
  'sasl.username': os.getenv("CONFLUENT_SASL_USERNAME"),
  'sasl.password': os.getenv("CONFLUENT_SASL_PASSWORD"),
})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
      print('Message delivery failed: {}'.format(err))
    else:
      print('Message delivered to {} on partition [{}]'.format(msg.topic(), msg.partition())) #NOSONAR

transactions = [
    {'id': 1, 'amount': 200.5},
    {'id': 2, 'amount': 100.5},
    {'id': 3, 'amount': 70.0,},
]

for data in transactions:
    # producer ----
    # Trigger any available delivery report callbacks from previous produce() calls
    producer.poll(0)

    # Asynchronously produce a message, the delivery report callback
    # will be triggered from poll() above, or flush() below, when the message has
    # been successfully delivered or failed permanently.
    producer.produce('transactions', json.dumps(data), callback=delivery_report)


# # Wait for any outstanding messages to be delivered and delivery report
# # callbacks to be triggered.
producer.flush()
