import time
from typing import Optional
from kafka import KafkaConsumer
from dotenv import load_dotenv
import os
import io
import avro.schema
import avro.io
import avro.datafile
from fastavro import schemaless_writer, schemaless_reader, parse_schema
import requests
import click
import json

load_dotenv()

BASE_URL = "https://{}:{}@{}".format(os.getenv("AIVEN_SASL_USERNAME"), os.getenv("AIVEN_SASL_PASSWORD"), os.getenv("AIVEN_SCHEMA_REGISTRY_URL"))

@click.group()
def main():
    """
    Simple CLI for manage the aiven avro consumers
    """
    pass

@main.command()
@click.option('--name', help='Consumer name.', required=True)
@click.option('--group', help='Consumer group name.', default="dev.consumers.avro")
def create(name, group):
    """This command create a consumer avro"""
    click.echo(
        "Creating consumer avro with name: {} and group: {}".format(name, group)
    )
    response = requests.post(
        BASE_URL + "/consumers/{}".format(group),
        headers={"Content-Type": "application/vnd.kafka.v2+json", "Accept": "application/vnd.kafka.v2+json"},
        json={
            "name": name,
            "format": "avro",
            "auto.offset.reset": "earliest"
        }
    )
    click.echo(response.json())

@main.command()
@click.option('--name', help='Consumer name.', required=True)
@click.option('--topic', help='Topic to subscribe.', required=True)
@click.option('--group', help='Consumer group name.', default="dev.consumers.avro")
def subscribe(name, topic, group):
    """This command subscribe a consumer to a specific topic"""
    click.echo(
        "Subscribing consumer avro with name: {} and group: {} to the topic {}".format(name, group, topic)
    )
    
    response = requests.post(
        BASE_URL + "/consumers/{}/instances/{}/subscription".format(group, name),
        headers={"Content-Type": "application/vnd.kafka.v2+json"},
        json={
            "topics": [topic],
        }
    )
    
    if response.status_code != 404:
        click.echo("Subscribed successfully")
        print(response.json())
    else:
        click.echo("Somethin went wron")
        print(response)
    # click.echo("subscribed successfully")

@main.command()
@click.option('--name', help='Consumer name.', required=True)
@click.option('--topic', help='Topic to subscribe.', required=True)
@click.option('--group', help='Consumer group name.', default="dev.consumers.avro")
def listen(name, topic, group):
    """This command keep listening to a specific topic"""
    click.echo(
        "Listening topic {} with user: {} and group: {}".format(topic, name, group)
    )
    
    while True:
        response = requests.get(
            BASE_URL + "/consumers/{}/instances/{}/records?timeout=3000".format(group, name),
            headers={"Accept": "application/vnd.kafka.avro.v2+json"},
        )

        click.echo(response.json())

        time.sleep(5)

# consumer = KafkaConsumer(
#     "orders",
#     # bootstrap_servers="kafka-aiven_kafka_1:9092" # dev,
#     group_id="aiven-consumer-avro-py",

#     # prod
#     bootstrap_servers=os.getenv("AIVEN_BOOTSTRAP_SERVER"), #prod 
#     security_protocol="SASL_SSL",
#     sasl_mechanism="PLAIN",
#     sasl_plain_username=os.getenv("AIVEN_SASL_USERNAME"),
#     sasl_plain_password=os.getenv("AIVEN_SASL_PASSWORD"),
#     ssl_cafile="ca.pem",

#     auto_offset_reset="earliest"
# )

# schema = avro.schema.parse(open("./src/aiven/order.avsc", "rb").read())

# value = b'\x00\x00\x00\x00\x04\xde\x01\x94\xce\x81Z\x0eGleba E'

# def bytes_to_string(raw_bytes):
#     bytes_reader = io.BytesIO(raw_bytes)
#     decoder = avro.io.BinaryDecoder(bytes_reader)
#     reader = avro.io.DatumReader(schema)
#     value = reader.read(decoder)
#     print(value)
    
# print("Consumer running")

# consumer.subscribe(["orders"])

# class WrapperIO(io.BytesIO):
#     def __enter__(self):
#         return self

#     def __exit__(self, *args):
#         self.close()
#         return False

# def avro_deserializer(schema, stream):
#     with WrapperIO(stream) as input:
#         if input is not None:
#             res = schemaless_reader(input, schema)
#             print(res)

# for msg in consumer:
#     print(msg)
    # avro_deserializer(schema, msg.value)

if __name__ == "__main__":
    main()