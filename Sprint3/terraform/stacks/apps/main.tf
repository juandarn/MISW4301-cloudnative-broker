###########################################################
# Producer-Consumer Stack Configuration
###########################################################

module "eks_cluster" {
  source = "../../modules/eks"

  cluster_name                   = var.cluster_name
  k8s_cluster_version            = var.k8s_cluster_version
  cluster_endpoint_public_access = true
}

module "sqs_queue" {
  source     = "../../modules/sqs"
  queue_name = var.queue_name
}

module "consumer" {
  source        = "../../modules/lambda"
  lambda_name   = var.consumer_config.lambda_name
  zip_file_path = "../../../consumer-lambda.zip"
  handler       = "src.entrypoints.queue.main.handler"
  env_variables = var.consumer_config.env_variables
}

# Create an event source mapping to connect the SQS queue to the consumer Lambda.
# This configures Lambda to automatically pull messages from the SQS queue.
resource "aws_lambda_event_source_mapping" "consumer_mapping" {
  event_source_arn = module.sqs_queue.sqs_queue_arn
  function_name    = module.consumer.lambda_name
  batch_size       = var.number_of_messages_to_process
  enabled          = true
}

module "first_subscriber" {
  source        = "../../modules/lambda"
  lambda_name   = "first-${var.subscriber_config.lambda_name}"
  zip_file_path = "../../../subscriber-lambda.zip"
  handler       = "src.entrypoints.topic.main.handler"
  env_variables = var.subscriber_config.env_variables
}

module "sns_topic" {
  source     = "../../modules/sns"
  topic_name = var.topic_name
  subscribers = {
    first_subscriber = module.first_subscriber.lambda_function_arn
  }
}

resource "aws_lambda_permission" "allow_sns_first_subscriber" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = module.first_subscriber.lambda_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.sns_topic.sns_topic_arn
}