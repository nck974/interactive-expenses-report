"""
Generate the report using jinja
"""
import os
from datetime import datetime
from typing import Any

from jinja2 import Environment, FileSystemLoader
from lib.graphs import HTMLGraph

from settings import CURRENCY, OUTPUT_DIR, TITLE


def generate_report(
    graphs_overview: list[HTMLGraph],
    graphs_category_details: list[HTMLGraph],
    graphs_category_avg: list[HTMLGraph],
    year_expenses: dict[str, Any],
) -> None:
    """
    Generate a report using jinja with the values provided from other report.add()
    The report will be generated in the folder provided in the settings file which shall be placed
    inside the project
    """
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    # Get template
    templates_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report.html")

    # Set report output
    date_today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(root, OUTPUT_DIR, f"{date_today}-report.html")

    with open(filename, "w", encoding="utf8") as file_handle:
        file_handle.write(
            template.render(
                title=TITLE,
                graphs_overview=graphs_overview,
                graphs_category_details=graphs_category_details,
                graphs_category_avg=graphs_category_avg,
                year_expenses=year_expenses,
                currency=CURRENCY,
            )
        )
    print(f"Document saved in {filename}")
