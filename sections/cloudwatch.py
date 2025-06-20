# cloudwatch.py
import boto3
import datetime
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    region = config["aws"]["region"]
    session = boto3.Session(
        profile_name=profile if profile else None, region_name=region
    )
    client = session.client("cloudwatch")

    now = datetime.datetime.utcnow()
    yesterday = now - datetime.timedelta(days=1)

    alarms = client.describe_alarms(StateValue="ALARM")["MetricAlarms"]
    rows = []

    for alarm in alarms:
        last_updated = alarm["StateUpdatedTimestamp"]
        if last_updated >= yesterday:
            rows.append(
                [
                    alarm["AlarmName"],
                    alarm["MetricName"],
                    alarm["StateValue"],
                    last_updated.strftime("%Y-%m-%d %H:%M UTC"),
                ]
            )

    if not rows:
        return "CloudWatch Alarms:\nNo alarms triggered in the last 24h."

    table = tabulate(
        rows, headers=["Name", "Metric", "State", "Updated"], tablefmt="simple_grid"
    )
    lines = [
        "CloudWatch Alarms (Last 24h):",
        f"[https://{config['aws'].get('region')}.console.aws.amazon.com/cloudwatch/home#alarmsV2:]",
        table,
    ]

    return "\n".join(lines)
