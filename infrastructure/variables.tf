variable "aiven_api_token" {
   description = "Aiven console API token"
   type = string
}

variable "project_name" {
   description = "Aiven console project name"
   type        = string
   default = "gabriel-sandbox"
}

variable "service_name" {
   description = "Aiven service name"
   type        = string
   default = "kafka-service"
}