"""
Script to process the data included in the CSV
"""
import os
import re


from lib.graphs import (
    get_all_categories_avg_expense_per_year_bar_graphs,
    get_overview_graphs,
    get_all_categories_detailed_bar_graphs)
from lib.html_report import generate_report
from lib.stats import get_year_expenses_by_category_with_subcategory
from lib.transaction import read_transactions

from settings import INPUT_DIR


def get_input_files():
    """
    Get all the CSV files stored in INPUT_DIR, this allows to do partial exports periodically
    without relying on exporting all the old data
    """
    root = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(root, INPUT_DIR)
    csv_files = []
    for file in os.listdir(input_dir):
        if re.search(r'.csv$', file):
            csv_files.append(os.path.join(input_dir, file))
    if not csv_files:
        raise ValueError(f'No *.csv files where found in {input_dir}')

    return csv_files


def main():
    """
    Main functionality of this project
    """
    transactions = read_transactions(get_input_files())

    overview_graphs = get_overview_graphs(transactions)
    category_details_graphs=get_all_categories_detailed_bar_graphs(transactions)
    category_avg_graphs=get_all_categories_avg_expense_per_year_bar_graphs(transactions)
    year_expenses = get_year_expenses_by_category_with_subcategory(transactions)

    generate_report(
        graphs_overview=overview_graphs,
        graphs_category_details=category_details_graphs,
        graphs_category_avg=category_avg_graphs,
        year_expenses=year_expenses
    )

if __name__ == '__main__':
    main()
