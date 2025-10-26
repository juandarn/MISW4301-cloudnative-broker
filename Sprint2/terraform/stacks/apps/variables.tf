variable "region" {
  type    = string
  default = "us-east-1"
}

variable "owner" {
  description = "Owner tag for resources"
  type        = string
  nullable    = false
}

variable "consumer_config" {
  description = "Configuration for the consumer lambda function"
  type        = object({
    lambda_name     = string
    repository_name = string
    image_version   = string
    env_variables   = map(string)
  })
}

variable "queue_name" {
  description = "Name of the SQS queue"
  type        = string
  nullable    = false
}

variable "number_of_messages_to_process" {
  description = "Number of messages to process in each batch for the consumer Lambda"
  type        = number
}

variable "cluster_name" {
  description = "El nombre del clúster EKS."
  type        = string
}

variable "k8s_cluster_version" {
  description = "La versión de Kubernetes para el clúster EKS."
  type        = string
}

variable "topic_name" {
  description = "Name of the SNS topic"
  type        = string
  nullable    = false
}

variable "subscriber_config" {
  description = "Configuration for the subscriber lambda function"
  type        = object({
    lambda_name     = string
    repository_name = string
    image_version   = string
    env_variables   = map(string)
  })
}