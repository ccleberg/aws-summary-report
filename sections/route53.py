# route53.py
import boto3
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    region = config["aws"]["region"]  # Not used by Route53, but kept for consistency

    session = boto3.Session(profile_name=profile if profile else None)
    client = session.client("route53")

    health_checks = client.list_health_checks()["HealthChecks"]
    rows = []

    for hc in health_checks:
        hc_id = hc["Id"]
        name = hc.get("HealthCheckConfig", {}).get(
            "FullyQualifiedDomainName", "Unnamed"
        )
        status = client.get_health_check_status(HealthCheckId=hc_id)
        status_summary = status["HealthCheckObservations"]
        healthy = all(
            obs["StatusReport"]["Status"].startswith("Success")
            for obs in status_summary
        )
        state = "HEALTHY" if healthy else "UNHEALTHY"
        rows.append([name, state])

    if not rows:
        return "Route 53 Health Checks:\nNo health checks configured."

    table = tabulate(rows, headers=["Domain", "Status"], tablefmt="simple_grid")
    lines = [
        "Route 53 Health Checks:",
        f"[https://{config['aws'].get('region')}.console.aws.amazon.com/route53/v2/healthchecks/home]",
        table,
    ]

    return "\n".join(lines)
