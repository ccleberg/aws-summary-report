# s3.py
import boto3
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    session = boto3.Session(profile_name=profile if profile else None)
    client = session.client("s3")

    buckets = client.list_buckets()["Buckets"]
    rows = []

    for bucket in buckets:
        name = bucket["Name"]
        public = "Unknown"
        encrypted = "No"

        try:
            acl = client.get_bucket_acl(Bucket=name)
            public = any(
                grant["Grantee"].get("URI", "").endswith("AllUsers")
                for grant in acl["Grants"]
            )
        except Exception:
            public = "Error"

        try:
            enc = client.get_bucket_encryption(Bucket=name)
            rules = enc["ServerSideEncryptionConfiguration"]["Rules"]
            if rules:
                encrypted = "Yes"
        except client.exceptions.ClientError:
            encrypted = "No"

        rows.append([name, "Yes" if public else "No", encrypted])

    table = tabulate(
        rows, headers=["Bucket", "Public", "Encrypted"], tablefmt="simple_grid"
    )
    lines = [
        "S3 Bucket Access Summary:",
        f"[https://{config['aws'].get('region')}.console.aws.amazon.com/s3/home]",
        table,
    ]

    return "\n".join(lines)
