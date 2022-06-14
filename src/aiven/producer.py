from typing import Optional
from fastapi import FastAPI
from kafka import KafkaProducer, Serializer
from pydantic import BaseModel
import json
from dotenv import load_dotenv
import os

import uvicorn

load_dotenv()

app = FastAPI()

class Message(BaseModel):
    message: dict
    topic: str
    user: Optional[str] = None
    password: Optional[str] = None

@app.post("/")
async def root(item: Message):
    try:
        producer = Producer(
            user=item.user,
            password=item.password,
        )

        producer.publish_message(
            message=item.message,
            topic=item.topic
        )
        
        return {"success": True}
    except Exception as err:
        return {"success": False, "error": str(err)}

class Producer:
    producer: KafkaProducer
    user: str

    def __init__(self, user: Optional[str], password: Optional[str]) -> None:
        self.user = user if user is not None else os.getenv("AIVEN_SASL_USERNAME")

        self.producer = KafkaProducer(
            # bootstrap_servers="kafka-aiven_kafka_1:9092", #dev
            client_id="aiven-producer-pyx",
            acks=0,
            retries=3,
            max_in_flight_requests_per_connection=1,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),

            # prod
            bootstrap_servers=os.getenv("AIVEN_BOOTSTRAP_SERVER"), #prod 
            security_protocol="SASL_SSL",
            sasl_mechanism="PLAIN",
            sasl_plain_username=self.user,
            sasl_plain_password=password if password is not None else os.getenv("AIVEN_SASL_PASSWORD"),
            ssl_cafile="ca.pem"
        )
    
    def publish_message(
        self,
        message: dict,
        topic: str
    ) -> None: 
        self.producer.send(
            topic,
            message,
            key=b"some.key",
            headers=[
                ('wex.event_name', b'transaction-created'),
                ('wex.producer_name', self.user.encode('utf-8')),
                #('wex.schema.subject', b'customer.new'),
                #('wex.schema.version', b'1.0.0'),
            ],
        ).add_callback(self._on_send_success).add_errback(self._on_send_error)

        self.producer.flush()

    def _on_send_success(self, record_metadata):
        print(record_metadata)
        print(f"{record_metadata.topic}/partition={record_metadata.partition}/offset={record_metadata.offset}")

    def _on_send_error(self, exception):
        print(exception)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)