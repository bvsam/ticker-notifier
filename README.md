# ticker-notifier

## About

An AWS EventBridge chron job that triggers a Lambda function to send an email notification to a list of recipient email addresses when certain tickers have fallen a set percentage from their yearly highs.

## Usage

1. Install the dependencies required for the lambda function. These dependencies must be installed for the `manylinux2014_x86_64` architecture to `layers/layer1/python` to allow for the `layers/layer1/python` directory to be zipped and uploaded as a AWS Lambda layer.

```bash
pip install -r requirements.txt --platform manylinux2014_x86_64 -t layers/layer1/python --only-binary=:all:
```

If you run into an error running the command above, run the command below on an Ubuntu 22.04 system (this can be done by running a Docker container with a bind mount).

```bash
pip install -r requirements.txt -t layers/layer1/python
```

2. Run `layers.py` to separate dependencies into 2 Lambda layers (at paths `layers/layer1/python` and `layers/layer2/python`) to prevent hitting the 50MB upload limit for AWS Lambda functions.

```bash
python3 layers.py
```

4. Create a `.tfvars` file at `src/main.tfvars`. Fill out the `.tfvars` file with all the required variables, which can be seen in `main.tf`. An example of what a `main.tfvars` file might look like is provided below.

```
deployment_name = "ticker-notifier"
region = "us-east-1"
sender_email = "name@example.com"
recipient_emails = "[\"name@example.com\"]"
eventbridge_schedule_expression = "rate(1 day)" # Or "cron(0 16 ? * 2 *)" to run every Monday at 16:00 UTC
```

Ensure that the `sender_email` is a verified email address and that the `recipient_emails` can receive emails from the sender. As an example, you can setup your AWS SES to send emails from your personal email (e.g. Gmail) to your personal email, after it's been verified. This must be manually setup using the AWS console before the terraform code can be applied.

4. Create a YAML config file for the Lambda function at `src/lambda/config.yaml`. Fill out the config file with valid configuration (an example is provided at `src/lambda/example_config.yaml`).

5. Initialize terraform and apply the terraform code. Within the `src/` directory, run the following:

```bash
terraform init
# Optional: terraform plan --var-file=main.tfvars
terraform apply --var-file=main.tfvars
```
