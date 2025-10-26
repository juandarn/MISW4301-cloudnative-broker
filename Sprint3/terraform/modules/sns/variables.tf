variable "topic_name" {
  description = "The name for the SNS topic."
  type        = string
}

variable "subscribers" {
  description = "List of SNS Topic ARNs to subscribe to the SNS topic."
  type        = map(string)
  default     = {}
}