terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.71.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.6.0"
    }
  }
}

provider "aws" {
  region = var.region
}

################################################################################
# Input variable definitions
################################################################################

variable "region" {
  type = string
}

variable "sender_email" {
  type = string
}

# JSON encoded list of recipient emails
variable "recipient_emails" {
  type = string
}

variable "eventbridge_schedule_expression" {
  type = string
}

################################################################################
# Resource definitions
################################################################################

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_ses_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_policy" "ses_policy" {
  name        = "ses_policy"
  description = "A policy to allow Lambda to send emails using SES"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ses_policy" {
  policy_arn = aws_iam_policy.ses_policy.arn
  role       = aws_iam_role.lambda_exec_role.name
}

data "archive_file" "lambda_inline_zip" {
  type        = "zip"
  output_path = "/tmp/lambda_zip_inline.zip"
  source_dir  = "${path.module}/lambda"
}

resource "aws_lambda_function" "ses_email_function" {
  function_name = "ses_email_function"
  role          = aws_iam_role.lambda_exec_role.arn

  timeout          = 60
  runtime          = "python3.10"
  handler          = "lambda.lambda_handler"
  filename         = data.archive_file.lambda_inline_zip.output_path
  source_code_hash = data.archive_file.lambda_inline_zip.output_base64sha256

  environment {
    variables = {
      REGION           = var.region
      SENDER_EMAIL     = var.sender_email
      RECIPIENT_EMAILS = var.recipient_emails
    }
  }
}

# EventBridge Rule to trigger the Lambda function
resource "aws_cloudwatch_event_rule" "chron_schedule" {
  name                = "trigger_lambda_chron_schedule"
  schedule_expression = var.eventbridge_schedule_expression
}

# Permission to allow EventBridge to invoke the Lambda function
resource "aws_lambda_permission" "eventbridge_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ses_email_function.function_name
  principal     = "events.amazonaws.com"

  source_arn = aws_cloudwatch_event_rule.chron_schedule.arn
}

# EventBridge Target to trigger the Lambda function
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.chron_schedule.name
  target_id = "lambda_target"
  arn       = aws_lambda_function.ses_email_function.arn
}
