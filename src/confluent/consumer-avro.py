from confluent_kafka import avro
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from dotenv import load_dotenv
import os

load_dotenv() 

class StringKeyAvroConsumer(AvroConsumer):

    def __init__(self, config):
        super(StringKeyAvroConsumer, self).__init__(config)

    def poll(self, timeout=None):
        """
        This is an overriden method from AvroConsumer class. This handles message
        deserialization using avro schema for the value only.

        @:param timeout
        @:return message object with deserialized key and value as dict objects
        """
        if timeout is None:
            timeout = -1
        message = super(AvroConsumer, self).poll(timeout)

        if message is None:
            return None

        if not message.value() and not message.key():
            return message
        
        if not message.error():
            if message.value() is not None:
                decoded_value = self._serializer.decode_message(message.value())
                message.set_value(decoded_value)

        return message

value_schema = avro.load('./src/confluent/order.avsc')

consumer = StringKeyAvroConsumer({
    'bootstrap.servers': os.getenv("CONFLUENT_BOOTSTRAP_SERVER"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("CONFLUENT_SASL_USERNAME"),
    'sasl.password': os.getenv("CONFLUENT_SASL_PASSWORD"),
    'schema.registry.url': os.getenv("CONFLUENT_SCHEMA_REGISTRY_URL"),
    'schema.registry.basic.auth.credentials.source': 'USER_INFO',
    'schema.registry.basic.auth.user.info': '{}'.format(os.getenv("CONFLUENT_SCHEMA_REGISTRY_AUTH_USER_INFO")),

    'group.id': 'group-x',
    'client.id': 'kakfa-avro-app',
    'auto.offset.reset': 'earliest',
    'session.timeout.ms': 45000
})

consumer.subscribe(['orders'])

while True:
    try:
        msg = consumer.poll(1)

    except SerializerError as e:
        print("Message deserialization failed for {}: {}".format(msg, e))
        break

    if msg is None:
        continue

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        continue

    print(msg.value())
