resource "aws_sqs_queue" "main" {
  name                       = var.queue_name
  delay_seconds              = 0
  max_message_size           = 262144 # 256 KB
  message_retention_seconds  = 3600 # 1 hour
  receive_wait_time_seconds  = 5
  visibility_timeout_seconds = 10
}

#############################################################
# IMPORTANT: This pollicy allows all actions on the SQS queue.
# It is recommended to restrict this policy to specific actions
# and principals in production environments.
# This is a bad practice and should only be used for testing purposes.
#############################################################

data "aws_iam_policy_document" "allow" {
  statement {
    sid    = "First"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["sqs:*"]
    resources = [aws_sqs_queue.main.arn]
  }
}

resource "aws_sqs_queue_policy" "test" {
  queue_url = aws_sqs_queue.main.id
  policy    = data.aws_iam_policy_document.allow.json
}