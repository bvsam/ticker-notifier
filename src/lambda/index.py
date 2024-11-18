import datetime as dt
import json
import os

import boto3  # type: ignore
import yaml
import yfinance as yf


def lambda_handler(event, context):
    # Determine which tickers require notifying
    config_fname = "config.yaml"
    with open(config_fname) as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config: {e}")
            return {"statusCode": 500, "body": "Failed to parse YAML config!"}

    is_decimal = config["decimal"]
    ticker_config = config["tickers"]
    use_close_high = config["use_close_high"]

    differences = {}
    alerts = {}
    for ticker in ticker_config.keys():
        y_ticker = yf.Ticker(ticker)
        yearly_high = (
            y_ticker.history(period="1y")["Close"].max()
            if use_close_high
            else y_ticker.info["fiftyTwoWeekHigh"]
        )
        difference = y_ticker.info["previousClose"] / yearly_high
        differences[ticker] = difference
        config_difference = ticker_config[ticker]
        if not is_decimal:
            config_difference /= 100
        alerts[ticker] = difference <= config_difference

    # Exit early if no tickers require notifying
    if not any(list(alerts.values())):
        print("No emails needed to be sent!")
        return {"statusCode": 200, "body": f"No emails needed to be sent!"}

    # Generating the email body
    body_text = f"The following tickers raised notifications at {dt.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S %z')}:\n"

    for ticker, should_alert in alerts.items():
        if should_alert:
            body_text += f"- {ticker}: {differences[ticker]*100:.2f}% (threshold {ticker_config[ticker]:.2f}%)\n"

    # Create a new SES client
    ses_client = boto3.client("ses", region_name=os.environ["REGION"])

    # Define email parameters
    sender_email = os.environ["SENDER_EMAIL"]  # Fetch from environment variables
    recipient_emails = json.loads(os.environ["RECIPIENT_EMAILS"])
    subject = "Ticker Notifier"

    # Send the email
    try:
        ses_client.send_email(
            Source=sender_email,
            Destination={
                "ToAddresses": recipient_emails,
            },
            Message={
                "Subject": {
                    "Data": subject,
                },
                "Body": {
                    "Text": {
                        "Data": body_text,
                    },
                },
            },
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"statusCode": 500, "body": f"Failed to send SES email! Error: {e}"}

    print("Successfully sent emails to recipients!")
    return {"statusCode": 200, "body": f"Email sent to {recipient_emails}!"}
