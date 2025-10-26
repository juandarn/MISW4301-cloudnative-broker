# Data sources removed - using ZIP packages instead of container images

data "aws_iam_role" "lambda_role" {
  name = "LabRole"
}

#Permissions for the lambda function
data "aws_iam_policy_document" "lambda_permissions" {
  # disabled for academical reasons
  #checkov:skip=CKV_AWS_111: "Ensure IAM policies does not allow write access without constraints"
  #checkov:skip=CKV_AWS_356: "Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions"

  #Permissions to record logs on CloudWatch
  statement {
    sid = "LambdaLogsCreatePutLogsPolicy"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect = "Allow"
    #TODO: wildcard must be removed
    resources = ["*"]
  }

  # ECR permissions removed - using ZIP packages instead of container images
}