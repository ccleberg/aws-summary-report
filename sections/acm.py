# acm.py
import boto3
from datetime import datetime, timedelta, timezone
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    region = config["aws"]["region"]
    session = boto3.Session(
        profile_name=profile if profile else None, region_name=region
    )
    client = session.client("acm")

    today = datetime.now(timezone.utc)
    deadline = today + timedelta(days=30)

    certs = client.list_certificates(CertificateStatuses=["ISSUED"])[
        "CertificateSummaryList"
    ]
    rows = []

    for cert in certs:
        detail = client.describe_certificate(CertificateArn=cert["CertificateArn"])[
            "Certificate"
        ]
        not_after = detail.get("NotAfter")
        if not_after and today <= not_after <= deadline:
            rows.append([cert["DomainName"], not_after.strftime("%Y-%m-%d")])

    if not rows:
        return "Expiring TLS Certificates:\nNo certs expiring in the next 30 days."

    table = tabulate(rows, headers=["Domain", "Expires"], tablefmt="simple_grid")
    lines = [
        "Expiring TLS Certificates (Next 30 Days):",
        f"[https://{config['aws'].get('region')}.console.aws.amazon.com/acm/home#/certificates/list]",
        table,
    ]

    return "\n".join(lines)
