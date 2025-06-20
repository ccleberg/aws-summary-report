# cloudfront.py
import boto3
from datetime import datetime, timedelta, timezone
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    session = boto3.Session(profile_name=profile if profile else None)
    client = session.client("cloudfront")

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=2)

    dists = client.list_distributions().get("DistributionList", {}).get("Items", [])
    rows = []

    for dist in dists:
        last_mod = dist["LastModifiedTime"]
        if last_mod >= cutoff:
            rows.append(
                [dist["Id"], dist["DomainName"], last_mod.strftime("%Y-%m-%d %H:%M")]
            )

    if not rows:
        return "CloudFront Changes:\nNo distributions changed in the last 48h."

    table = tabulate(
        rows, headers=["ID", "Domain", "Last Modified"], tablefmt="simple_grid"
    )
    lines = [
        "CloudFront Distribution Changes (Last 48h):",
        f"[https://{config['aws'].get('region')}.console.aws.amazon.com/cloudfront/v4/home#/distributions]",
        table,
    ]

    return "\n".join(lines)
