# ticker-notifier

## About

An AWS EventBridge chron job that triggers a Lambda function to send an email notification to a list of email addresses when certain tickers have fallen a set percentage from their yearly highs.

## Usage

1. Install the dependencies required for the lambda function. These dependencies must be installed to `src/lambda/` to allow for the `src/lambda/` directory to be zipped and run as a AWS Lambda function.

```
pip install -r requirements.txt -t src/lambda/
```

2. Create a `.tfvars` file at `src/main.tfvars`. Fill out the `.tfvars` file with all the required variables, which can be seen in `main.tf`. An example of what a `main.tfvars` file might look like is provided below.

```
deployment_name = "ticker-notifier"
region = "us-east-1"
sender_email = "name@example.com"
recipient_emails = "[\"name@example.com\"]"
eventbridge_schedule_expression = "rate(1 day)"
```

Ensure that the `sender_email` is a verified email address and that the `recipient_emails` can receive emails from the sender. As an example, you can setup your AWS SES to send emails from your personal email (e.g. Gmail) to your personal email, after it's been verified. This must be manually setup using the AWS console before the terraform code can be applied.

3. Create a YAML config file for the Lambda function at `src/lambda/config.yaml`. Fill out the config file with valid configuration (an example is provided at `src/lambda/example_config.yaml`).

4. Apply the terraform code. Within the `src/` directory, run the following:

```
terraform apply --var-file=main.tfvars
```
