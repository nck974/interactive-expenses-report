"""
Generate an example CSV file with random transactions
"""

from datetime import datetime, timedelta
import os
from random import randint
import random
from  lib.transaction import Transaction

CATEGORIES = [
    {"name": 'Car', 'subcategories': ['Maintenance', 'Petrol', 'Taxes'] },
    {"name": 'Flat', 'subcategories': ['Rent', 'Maintenance', 'Electricity'] },
    {"name": 'Food', 'subcategories': ['Supermarket', 'Restaurants', 'Coffee'] },
    {"name": 'Transport', 'subcategories': ['Train', 'Plane', 'Bus'] },
]

START_DATE = datetime(2018, 1, 1, 1, 1, 1)
END_DATE = datetime(2023, 1, 1, 1, 1, 1)



def daterange(start_date, end_date):
    """
    See: https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
    """
    for day in range(int((end_date - start_date).days)):
        yield start_date + timedelta(day)

transactions: list[Transaction] = []


def main():
    """
    Main functionality
    """
    for single_date in daterange(START_DATE, END_DATE):

        cat_nr = randint(0, len(CATEGORIES)-1)
        cat = CATEGORIES[cat_nr]
        subcat_nr = randint(0, len(cat['subcategories'])-1)

        category = cat['name']
        subcategory = cat['subcategories'][subcat_nr]
        value = random.uniform(-50, -0.01)

        transactions.append(Transaction(
            Date=single_date.strftime("%d/%m/%Y"),
            Description=f'Expense of {single_date.strftime("%Y-%m-%d")}',
            Value=value,
            Category=category,
            Subcategory=subcategory,
        ))


        # Add an income every 5 days
        if single_date.day % 5 == 0:
            transactions.append(
                Transaction(
                    Date=single_date.strftime("%d/%m/%Y"),
                    Description=f'Income of {single_date.strftime("%Y-%m-%d")}',
                    Value=random.uniform(1, 200),
                    Category='Salary',
                    Subcategory=None
                )
            )

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'input', 'example.csv')
    with open(filename, 'w', encoding='utf-16') as writer:

        # HEADER
        header = '"Date";"Description";"Value";"Account";"Category";"Subcategory";"Tags"\n'
        writer.write(header)

        # TRANSACTIONS
        for expense in transactions:

            csv_expense = f'{expense.date.strftime("%d/%m/%Y")};{expense.description};' + \
                f'{expense.value};{expense.account};{expense.category};{expense.subcategory};' + \
                f'{expense.tags}\n'
            writer.write(csv_expense)

if __name__ == '__main__':
    main()
