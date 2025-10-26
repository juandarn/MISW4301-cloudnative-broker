resource "aws_sns_topic" "main" {
  name = var.topic_name
}

# Conditionally subscribe a list of Lambda function to the SNS topic.
# This resource is ONLY created if at least one subscriber is provided.
resource "aws_sns_topic_subscription" "lambda_subscription" {
  for_each = var.subscribers
  topic_arn = aws_sns_topic.main.arn
  protocol  = "lambda"
  endpoint  = each.value
}

#############################################################
# IMPORTANT: This policy allows all components to publish on the SNS topic.
# It is recommended to restrict this policy to specific services
# or roles in production environments.
# This is a bad practice and should only be used for testing purposes.
#############################################################

resource "aws_sns_topic_policy" "default" {
  arn = aws_sns_topic.main.arn

  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  policy_id = "__publisher_subscriber_ID"

  statement {
    actions = [
      "SNS:Subscribe",
      "SNS:Receive",
      "SNS:Publish",
      "SNS:ListSubscriptionsByTopic",
      "SNS:GetTopicAttributes",
    ]

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [
      aws_sns_topic.main.arn,
    ]

    sid = "__publisher_subscriber_ID"
  }
}