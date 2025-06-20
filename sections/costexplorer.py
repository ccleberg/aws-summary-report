# costexplorer.py
import boto3
import datetime
from tabulate import tabulate


def get_section(config):
    profile = config["aws"].get("profile")
    region = config["aws"]["region"]

    session = boto3.Session(
        profile_name=profile if profile else None, region_name=region
    )
    client = session.client("ce")

    today = datetime.date.today()
    start = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    results = response["ResultsByTime"][0]
    date = results["TimePeriod"]["Start"]
    estimated = results.get("Estimated", False)

    rows = []
    groups = results.get("Groups", [])
    if groups:
        for group in groups:
            service = group["Keys"][0]
            cost = (
                group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", "0.00")
            )
            rows.append([service, f"${float(cost):.2f}"])
    else:
        rows.append(["No service-level data available", ""])

    total_cost = results.get("Total", {}).get("UnblendedCost", {}).get("Amount", None)
    if total_cost is None:
        total_cost = sum(
            float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0.0))
            for group in groups
        )
    rows.append(["TOTAL", f"${float(total_cost):.2f}"])

    table = tabulate(
        rows,
        headers=["Service", "Cost"],
        tablefmt="simple_grid",
        colalign=("left", "right"),
    )

    lines = [
        f"AWS Billing Report for {date}",
        f"[https://{config['aws'].get('region')}.console.aws.amazon.com/costmanagement/]",
        table,
    ]

    if estimated:
        lines.append("\nNote: Costs are estimated and may change.")

    return "\n".join(lines)
