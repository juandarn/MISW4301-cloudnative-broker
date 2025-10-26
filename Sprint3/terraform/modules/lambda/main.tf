# Lambda CloudWatcg log group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 30
}

resource "aws_lambda_function" "main" {
  # disabled for academical reasons
  function_name = var.lambda_name
  role          = data.aws_iam_role.lambda_role.arn
  package_type  = "Zip"
  filename      = var.zip_file_path
  handler       = var.handler
  runtime       = "python3.11"
  timeout       = 10

  environment {
    variables = var.env_variables
  }
}