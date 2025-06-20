# config.py
import boto3
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    region = config["aws"]["region"]
    session = boto3.Session(
        profile_name=profile if profile else None, region_name=region
    )
    client = session.client("config")

    paginator = client.get_paginator("describe_compliance_by_resource")
    page_iterator = paginator.paginate(ComplianceTypes=["NON_COMPLIANT"])

    rows = []

    for page in page_iterator:
        for result in page.get("ComplianceByResources", []):
            resource_type = result.get("ResourceType", "Unknown")
            resource_id = result.get("ResourceId", "Unknown")
            rows.append([resource_type, resource_id])

    if not rows:
        return "AWS Config Non-Compliance:\nAll resources are compliant."

    table = tabulate(
        rows, headers=["Resource Type", "Resource ID"], tablefmt="simple_grid"
    )
    lines = [
        "AWS Config Non-Compliant Resources:",
        f"[https://{config['aws'].get('region')}.console.aws.amazon.com/config/home#/resources?complianceType=NON_COMPLIANT]",
        table,
    ]

    return "\n".join(lines)
