# securityhub.py
import boto3
import datetime
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    region = config["aws"]["region"]

    session = boto3.Session(
        profile_name=profile if profile else None, region_name=region
    )
    client = session.client("securityhub")

    findings = []
    paginator = client.get_paginator("get_findings")

    response_iterator = paginator.paginate(
        Filters={
            "CreatedAt": [{"DateRange": {"Value": 1, "Unit": "DAYS"}}],
            "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}],
            "WorkflowStatus": [{"Value": "NEW", "Comparison": "EQUALS"}],
        },
    )

    for page in response_iterator:
        findings.extend(page.get("Findings", []))

    rows = []
    for finding in findings:
        title = finding.get("Title", "No title")
        severity = finding.get("Severity", {}).get("Label", "UNKNOWN")
        product = finding.get("ProductName", "Unknown Product")
        resource = finding.get("Resources", [{}])[0].get("Id", "Unknown Resource")
        rows.append([severity, title[:50], product, resource[:30]])

    if not rows:
        lines = [
            "AWS Security Hub Findings (Last 24h)",
            "No new findings in the past 24 hours.",
        ]
    else:
        table = tabulate(
            rows,
            headers=["Severity", "Title", "Product", "Resource"],
            tablefmt="simple_grid",
            colalign=("center", "left", "left", "left"),
        )
        lines = [
            f"AWS Security Hub Findings (Last 24h): {len(rows)} new finding(s)",
            f"[https://{config['aws'].get('region')}.console.aws.amazon.com/securityhub/home?region=eu-west-1#/findings]",
            table,
        ]

    return "\n".join(lines)
