output "api_endpoint" {
  value = module.eks_cluster.cluster_endpoint
}

output "sqs_queue_url" {
  value = module.sqs_queue.sqs_queue_url
}

output "sns_topic_arn" {
  value = module.sns_topic.sns_topic_arn
}