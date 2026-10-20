import os
import boto3

sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
THRESHOLD_PCT = float(os.environ.get("THRESHOLD_PCT", "0.3"))


def lambda_handler(event, context):
    """Triggered by DynamoDB Streams with a batch of new/changed items."""
    symbol = "LYFT"
    prices = []

    for record in event["Records"]:
        if record["eventName"] != "INSERT":
            continue
        item = record["dynamodb"]["NewImage"]
        price = item["price"]
        prices.append(float(price.get("N") or price.get("S"))) 
        symbol = item["symbol"]["S"]

    if len(prices) < 2:
        return "Not enough records in batch"

    first, last = prices[0], prices[-1]
    change_pct = (last - first) / first * 100

    if abs(change_pct) >= THRESHOLD_PCT:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"{symbol} anomaly",
            Message=f"{symbol} moved {change_pct:+.2f}% across the last {len(prices)} records "
                    f"({first:.2f} to {last:.2f}).",
        )
        return "Alert sent"
    return "No anomaly"