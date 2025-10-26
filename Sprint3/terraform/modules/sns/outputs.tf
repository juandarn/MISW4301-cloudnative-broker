output "sns_topic_arn" {
  description = "The ARN of the created SNS topic."
  value       = aws_sns_topic.main.arn
}

output "sns_topic_name" {
  description = "The name of the created SNS topic."
  value       = aws_sns_topic.main.name
}