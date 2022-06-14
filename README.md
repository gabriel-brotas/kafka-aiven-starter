
## Goal
    The purpose of this project is to learn how to setup and connect a producer and consumer to a Kafka cluster on Confluent or Aiven.

## Requirements
- Docker/Docker Compose

## How to use
1 - create your cluster on aiven or confluent and add the environment variables on a .env file with the following template
```
    CONFLUENT_BOOTSTRAP_SERVER=
    CONFLUENT_SCHEMA_REGISTRY_URL=
    CONFLUENT_SCHEMA_REGISTRY_AUTH_USER_INFO=
    CONFLUENT_SASL_USERNAME=
    CONFLUENT_SASL_PASSWORD=

    AIVEN_BOOTSTRAP_SERVER=
    AIVEN_SASL_USERNAME=
    AIVEN_SASL_PASSWORD=
    AIVEN_SCHEMA_REGISTRY_URL=
```

2 - Create the resource using docker-compose
```bash
docker-compose up -d
```

3 - Aiven

    3.0 - Create the cluster;
    3.1 - Enable the "kafka_authentication_methods.sasl" option;
    3.2 - Enable the "Apache Kafka REST API (Karapace)" and "Schema Registry (Karapace)" option;
    3.3 - Create the topic "transactions";
    3.3 - Access the container and run the following commands:
```bash
    # access the container
    docker exec -it kafka-app bash

    # run the producer
    pdm run aiven:p

    # send some message
    curl -X POST -H "Content-Type: application/json" \
        --data '{"message":{"orderId":2,"orderTime":123129305,"orderAddress":"my address"},"topic":"transactions"}' \
        http://localhost:3000

    # response = {"success":true}

    # read messages using consumer
    # open another terminal and access the container again
    docker exec -it kafka-app bash

    # run the consumer
    pdm run aiven:c

    # now when you send a message you should be able to see in the terminal
```
    3.4 - send messages with avro format
    3.4.1 - Create a "orders" topic and save the schema "src/aiven/order.avsc" on the value schema using the aiven UI
```bash
    # access the container
    docker exec -it kafka-app bash

    # run the avro producer
    pdm run aiven:pa

    # send some message
    curl -X POST -H "Content-Type: application/json" \
        --data '{"schema_id":1,"topic":"orders","message":{"orderId":987,"orderTime":94385034,"orderAddress":"Parqu st b E"}}' \
        http://localhost:3000
    # response = {"success":true,"result":{"key_schema_id":null,"offsets":[{"offset":0,"partition":0}],"value_schema_id":1}}

    # read messages using avro consumer
    # open another terminal and access the container again
    docker exec -it kafka-app bash

    # avro consumer
    # create a consumer
    pdm run aiven:ca create --name=consumer-x

    # subscribe your costumer to a topic
    pdm run aiven:ca subscribe --name=consumer-x --topic=orders

    # wait 5 min so aiven can setup your customer and then listen the orders topic
    pdm run aiven:ca listen --name=consumer-x --topic=orders
```

4 - Confluent

    4.0 - Create the cluster;
    4.1 - Create a "transactions" topic;
    4.2 - Access the container and run the following commands;
```bash
    # access the container
    docker exec -it kafka-app bash

    # run the first confluent producer
    pdm run confluent:p

    # you should see a message similar to this:
    # Message delivered to transactions on partition [1]
    # Message delivered to transactions on partition [2]
    # Message delivered to transactions on partition [2]

    # read using consumer
    # open another terminal and access the container again
    docker exec -it kafka-app bash

    # run the consumer
    pdm run confluent:c

    # you should be able to read the messages
```
    4.3 - send message with avro
    4.3.1 - Create a "orders" topic and save the schema "src/confluent/order.avsc" on the value schema
```bash
    # access the container
    docker exec -it kafka-app bash

    # run the producer to send message on the order.avsc schema format
    pdm run confluent:pa

    # read using consumer
    # open another terminal and access the container again
    docker exec -it kafka-app bash

    # run the consumer
    pdm run confluent:ca

    # you should be able to read the messages
```  