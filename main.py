import toml
from utils import send_email
import importlib


def load_sections(section_names, config):
    report_parts = []

    for name in section_names:
        try:
            mod = importlib.import_module(f"sections.{name}")
            section_text = mod.get_section(config)
            report_parts.append(section_text)
        except Exception as e:
            report_parts.append(f"[ERROR loading section '{name}']: {e}")

    return "\n\n".join(report_parts)


def main():
    config = toml.load("config.toml")
    sections = config["report"]["sections"]

    body = load_sections(sections, config)

    send_email(
        smtp_config=config["email"],
        subject="AWS Daily Report",
        body=body,
        recipients=config["recipients"]["emails"],
    )

    # DEBUG
    # print(body)


if __name__ == "__main__":
    main()
