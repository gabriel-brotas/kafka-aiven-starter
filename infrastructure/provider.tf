terraform {
   required_providers {
      aiven = {
         source  = "aiven/aiven"
         version = ">= 2.6.0, < 3.0.0"
      }
   }
  #  backend "s3" {
  #    bucket = "bucket-name"
  #    key = "terraform.tfstate"
  #    region= "us-east-1"
  #  }
}

provider "aiven" {
   api_token = var.aiven_api_token
}

resource "aiven_kafka" "kafka-cluster" {
  project                 = var.project_name
  service_name            = var.service_name

  cloud_name              = "aws-us-east-1"
  plan                    = "startup-2"
  maintenance_window_dow  = "monday"
  maintenance_window_time = "10:00:00"

  karapace = true
  
  kafka_user_config {
    kafka_authentication_methods {
      sasl = true  
    }

    kafka_rest      = true
    # kafka_connect   = true
    schema_registry = true
    # kafka_version   = "2.4"
  
    kafka {
      group_max_session_timeout_ms = 70000
      log_retention_bytes          = 1000000000
    }

    public_access {
      kafka_rest    = true
      # kafka_connect = true
    }
  }
}

resource "aiven_service_user" "myserviceuser" {
  depends_on = [
    aiven_kafka.kafka-cluster
  ]
  project      = aiven_kafka.kafka-cluster.project
  service_name = aiven_kafka.kafka-cluster.service_name
  username     = "dev.sa.gabriel"
}

resource "aiven_kafka_acl" "mytestacl" {
  depends_on = [
    aiven_kafka.kafka-cluster
  ]

  project      = aiven_kafka.kafka-cluster.project
  service_name = aiven_kafka.kafka-cluster.service_name
  topic        = "dev.*"
  permission   = "admin"
  username     = "dev"
}

resource "aiven_kafka_topic" "transactions_topic" {
  depends_on = [
    aiven_kafka.kafka-cluster
  ]

  project      = aiven_kafka.kafka-cluster.project
  service_name = aiven_kafka.kafka-cluster.service_name
  topic_name             = "transactions"
  partitions             = 3
  replication            = 3
  termination_protection = true

  config {
    flush_ms                       = 10
    unclean_leader_election_enable = true
    cleanup_policy                 = "compact,delete"
  }


  timeouts {
    create = "1m"
    read   = "5m"
  }
}

resource "aiven_kafka_topic" "orders_topic" {
  depends_on = [
    aiven_kafka.kafka-cluster
  ]

  project      = aiven_kafka.kafka-cluster.project
  service_name = aiven_kafka.kafka-cluster.service_name
  topic_name             = "orders"
  partitions             = 3
  replication            = 3
  termination_protection = true

  config {
    flush_ms                       = 10
    unclean_leader_election_enable = true
    cleanup_policy                 = "compact,delete"
  }


  timeouts {
    create = "1m"
    read   = "5m"
  }
}


resource "aiven_kafka_schema" "order_schema" {
  depends_on = [
    aiven_kafka.kafka-cluster
  ]
  
  project      = aiven_kafka.kafka-cluster.project
  service_name = aiven_kafka.kafka-cluster.service_name
  subject_name        = "kafka-schema1"
  compatibility_level = "FORWARD"

  schema = <<EOT
    {
  "doc": "Sample schema to help you get started.",
  "name": "sampleRecord",
  "namespace": "com.mycorp.mynamespace",
  "type": "record",
  "fields": [
    {
      "doc": "The id of the order.",
      "name": "orderId",
      "type": "int"
    },
    {
      "doc": "Timestamp of the order.",
      "name": "orderTime",
      "type": "int"
    },
    {
      "doc": "The address of the order.",
      "name": "orderAddress",
      "type": "string"
    }
  ]
}
    EOT
}