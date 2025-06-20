def format_billing_info(results):
    date = results["TimePeriod"]["Start"]
    lines = [f"AWS Billing Report for {date}", "-" * 40]

    for group in results["Groups"]:
        service = group["Keys"][0]
        amount = group["Metrics"]["UnblendedCost"]["Amount"]
        lines.append(f"{service:<30} ${float(amount):>10.2f}")

    total = results["Total"]["UnblendedCost"]["Amount"]
    lines.append("-" * 40)
    lines.append(f"{'TOTAL':<30} ${float(total):>10.2f}")
    return "\n".join(lines)
