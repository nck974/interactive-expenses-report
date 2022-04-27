"""
Script to process the data included in the CSV
"""
import csv
import os
import re


from lib.graphs import (get_all_categories_avg_expense_per_year_bar_graphs, 
    get_overview_graphs, get_all_categories_detailed_bar_graphs)
from lib.html_report import generate_report
from lib.stats import get_year_expenses_by_category_with_subcategory
from lib.transaction import Transaction

from settings import INPUT_DIR


def remove_duplicated_transactions(transactions: list[Transaction]):
    """
    Remove duplicated transactions to be safe from overlapping exports. To consider a duplicate
    for the same date the value, category and description have to be the same.
    """
    seen_transactions = set()
    unique_list = []
    for transaction in transactions:
        unique = f'{transaction.date.isoformat()}-{transaction.description}' + \
            f'-{transaction.value}-{transaction.description}'
        if unique not in seen_transactions:
            unique_list.append(transaction)
            seen_transactions.add(unique)
        else:
            print(f'The following duplicate between files has been removed:\n -> "{unique}"')

    return unique_list


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


def read_transactions() -> list[Transaction]:
    """
    Read all transactions from a csv file and return them as a list of the pydantic model.
    """
    transactions = []
    csv_files = get_input_files()
    for csv_file in csv_files:
        with open(csv_file, mode='r',  encoding='utf-16') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                transactions.append( Transaction(**row) )

    if not transactions:
        raise ValueError('No transactions could be found in the CSV file')

    transactions = remove_duplicated_transactions(transactions)

    return transactions


def main():
    """
    Main functionality of this project
    """
    transactions = read_transactions()

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
