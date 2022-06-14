from typing import List, Optional
from fastapi import FastAPI
import json
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os

import uvicorn

load_dotenv()

app = FastAPI()

class Message(BaseModel):
    message: dict
    topic: str
    schema_id: int

    username: Optional[str] = None
    password: Optional[str] = None

@app.post("/")
async def root(item: Message):
    try:
        schema_registry = SchemaRegistry(
            username=item.username,
            password=item.password,
        )

        result = schema_registry.send_message(
            message=item.message,
            topic=item.topic,
            schema_id=item.schema_id
        )

        if "error_code" in result:
            raise Exception(result["message"])
        
        return {"success": True, "result": result}
    except Exception as err:
        return {"success": False, "error": str(err)}

class SchemaRegistry:
    url: str = None

    def __init__(self, username: Optional[str], password: Optional[str]) -> None:
        self.url = self._get_schema_registry_url(username, password)
        
    def get_subjects(self) -> List[str]:
        return requests.get(self.url + "/subjects").json()
    
    def get_subject_versions(self, subject: str) -> List[int]:
        return requests.get(self.url + "/subjects/" + subject + "/versions").json()
    
    def get_schema_by_id(self, id: int) -> str:
        return requests.get(self.url + "/schemas/ids/" + str(id)).json()
            
    
    def get_topics(self) -> List[str]:
        return requests.get(self.url + "/topics").json()

    def send_message(self, message: dict, topic: str, schema_id: int):
        schema = self.get_schema_by_id(schema_id)

        if 'schema' not in schema:
            raise Exception("Schema not found")

        body = {
            "value_schema_id": schema_id,
            "value_schema": json.loads(schema['schema']),
            "records": [ 
                {
                    "value": message
                }
            ]
        }

        return requests.post(
            self.url + "/topics/" + topic, 
            json=body, 
            headers={"Content-Type": "application/vnd.kafka.avro.v2+json"}
        ).json()

    def _get_schema_registry_url(self, username: Optional[str], password: Optional[str]) -> str:
        auth_user = username if username is not None else os.getenv("AIVEN_SASL_USERNAME")
        auth_password = password if password is not None else os.getenv("AIVEN_SASL_PASSWORD")

        return "https://" + auth_user + ":" + auth_password + "@" + os.getenv("AIVEN_SCHEMA_REGISTRY_URL")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)