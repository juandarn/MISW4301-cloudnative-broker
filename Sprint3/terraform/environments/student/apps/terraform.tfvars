region = "us-east-1"
owner  = "hv.lopez" # Use your university username.

cluster_name = "dann-cluster"
k8s_cluster_version = "1.33"

consumer_config = {
  lambda_name     = "consumer-application"
  repository_name = "consumer-lambda"
  image_version   = "1.0.0"
  env_variables   = {
    "LOG_LEVEL" = "INFO"
  }
}

queue_name = "producer-consumer-queue"
number_of_messages_to_process = 2

subscriber_config = {
  lambda_name     = "subscriber-application"
  repository_name = "subscriber-lambda"
  image_version   = "1.0.0"
  env_variables   = {
    "LOG_LEVEL" = "INFO"
  }
}

topic_name = "publisher-subscriber-topic"