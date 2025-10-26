variable "lambda_name" {
  description = "Lambda function name"
  type        = string
}

variable "zip_file_path" {
  description = "Path to the ZIP file containing the Lambda function code"
  type        = string
  nullable    = false
}

variable "handler" {
  description = "Lambda function handler"
  type        = string
  nullable    = false
}

variable "env_variables" {
  description = "Map object with environment variables for the lambda function. Empty by default."
  type        = map(string)
  default     = {}
}