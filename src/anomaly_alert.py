import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone

table = boto3.resource("dynamodb").Table("lyft-data")
sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
SYMBOL = "LYFT"
MINUTES = 10 
THRESHOLD_PCT = 0.3   

def lambda_handler(event, context):
    since = datetime.now(timezone.utc) - timedelta(minutes=MINUTES)
    items = table.query(
        KeyConditionExpression=Key("symbol").eq(SYMBOL)
        & Key("timestamp").gte(since.strftime("%Y-%m-%dT%H:%M:%SZ"))
    )["Items"]

    if len(items) < 2:
        return "Not enough data"

    first = float(items[0]["price"])
    last = float(items[-1]["price"])
    change_pct = (last - first) / first * 100

    if abs(change_pct) >= THRESHOLD_PCT:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"{SYMBOL} anomaly",
            Message=f"{SYMBOL} moved {change_pct:+.2f}% in the last {MINUTES} minutes "
                    f"({first:.2f} to {last:.2f}).",
        )
        return "Alert sent"
    return "No anomaly"