"""
This file takes charge of grouping and sorting all transactions to be plotted or represented
"""
from collections import OrderedDict
import datetime

from lib.transaction import Transaction


def _get_min_date(transactions: list[Transaction]):
    """
    Return the date of the oldest transaction
    """
    min_date: datetime = None
    for transaction in transactions:
        if min_date is None:
            min_date = transaction.date
        else:
            if min_date > transaction.date:
                min_date = transaction.date
    return min_date

def _get_max_date(transactions: list[Transaction]):
    """
    Return the date of the oldest transaction
    """
    max_date: datetime = None
    for transaction in transactions:
        if max_date is None:
            max_date = transaction.date
        else:
            if max_date < transaction.date:
                max_date = transaction.date
    return max_date

def get_timeline(transactions: list[Transaction]) -> list[str]:
    """
    Return a list of strings for each month of each year available in the transactions
    """
    min_date: datetime = _get_min_date(transactions)
    max_date: datetime = _get_max_date(transactions)

    timeline = []
    for year in range(min_date.year, max_date.year+1):
        for month in range(1,12+1):
            if year == min_date.year:
                if month < min_date.month:
                    continue
            if year == max_date.year:
                if month > max_date.month:
                    continue
            month_number = datetime.date(1900, month, 1).strftime('%m')
            timeline.append(f'{str(year)[-2:]}_{month_number}')

    return timeline


def get_monthly_total_expenses(transactions: list[Transaction]) -> dict[str: float]:
    """
    Get the total expenses by month of the given list of transactions
    """
    expenses = {}
    for transaction in reversed(transactions):

        if transaction.transaction_type != 'EXPENSE':
            continue

        date = f'{str(transaction.date.year)[-2:]}_{transaction.date.strftime("%m")}'
        if date in expenses:
            expenses[date] = expenses[date] + abs(transaction.value)
        else:
            expenses[date] = abs(transaction.value)

    timeline = get_timeline(transactions)
    for date in timeline:
        if not date in expenses:
            expenses[date] = 0

    expenses = dict(sorted(expenses.items()))

    return expenses


def get_monthly_total_income(transactions: list[Transaction]) -> dict[str: float]:
    """
    Get the total income by month of the given list of transactions
    """
    income = {}
    for transaction in reversed(transactions):

        if transaction.transaction_type != 'INCOME':
            continue

        date = f'{str(transaction.date.year)[-2:]}_{transaction.date.strftime("%m")}'
        if date in income:
            income[date] = income[date] + abs(transaction.value)
        else:
            income[date] = abs(transaction.value)

    timeline = get_timeline(transactions)
    for date in timeline:
        if not date in income:
            income[date] = 0

    income = dict(sorted(income.items()))

    return income


def get_income_expenses_balance(transactions: list[Transaction]) -> dict[str: float]:
    """
    Get difference between expenses and income per month
    """
    expenses = get_monthly_total_expenses(transactions)
    income = get_monthly_total_income(transactions)
    balance = {}
    for date, expense in expenses.items():
        income_value = income[date]
        balance[date] = income_value - abs(expense)
    return balance


def get_inc_exp_balance_percent(transactions: list[Transaction]) -> dict[str: float]:
    """
    Get difference between expenses and income per month
    """
    expenses = get_monthly_total_expenses(transactions)
    income = get_monthly_total_income(transactions)
    balance = {}
    for date, expense in expenses.items():
        income_value = income[date]
        if income_value == 0:
            balance[date] = 0
        else:
            balance[date] = (income_value - abs(expense)) / income_value * 100
    return balance


def get_metric_average(metrics: dict[str: float]) -> float|int:
    """
    Metric average
    """
    total = 0
    count=0
    for metric in metrics.values():
        total = total + metric
        count = count + 1
    return total/count


def __sort_categories_by_expense(expenses) -> list[str]:
    """
    Sort the categories from the one with more expenses to the least
    See: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    """
    category_total_expenses = {}
    for category in expenses.keys():
        for date in expenses[category]:
            if category in category_total_expenses:
                category_total_expenses[category] = category_total_expenses[category] + \
                    expenses[category][date]
            else:
                category_total_expenses[category] = expenses[category][date]
    category_total_expenses = OrderedDict(
        sorted(category_total_expenses.items(), key=lambda x: x[1], reverse=True))
    return category_total_expenses.keys()


def get_month_exp_by_category(transactions: list[Transaction]
        ) -> OrderedDict[str:dict[str:float]]:
    """
    Return a dict with the list of categories (without subcategories)
    """
    categories = []
    expenses = {}
    for transaction in reversed(transactions):

        if transaction.transaction_type != 'EXPENSE':
            continue

        date = f'{str(transaction.date.year)[-2:]}_{transaction.date.strftime("%m")}'
        category = transaction.category

        if not category in categories:
            categories.append(category)

        if not category in expenses:
            expenses[category] = {}

        if not date in expenses[category]:
            expenses[category][date] = abs(transaction.value)
        else:
            expenses[category][date] = expenses[category][date] + abs(transaction.value)


    # Fill empty categories
    timeline = get_timeline(transactions)
    for category, cat_expenses in expenses.items():
        for date in timeline:
            if not date in cat_expenses:
                cat_expenses[date] = 0


    # Sort by total amount spent
    sorted_categories = __sort_categories_by_expense(expenses)
    category_expenses = OrderedDict()
    for category in sorted_categories:
        category_expenses[category] = dict(sorted(expenses[category].items()))

    return category_expenses


def get_month_exp_by_category_with_subcategories(transactions: list[Transaction]):
    """
    Get monthly expenses with the details of the subcategories. If an expense does not have a
    subcategory a default 'No subcategory' will be created
    """
    expenses = {}
    for transaction in reversed(transactions):

        if transaction.transaction_type != 'EXPENSE':
            continue

        date = f'{str(transaction.date.year)[-2:]}_{transaction.date.strftime("%m")}'
        category = transaction.category
        subcategory = transaction.subcategory

        if not category in expenses:
            expenses[category] = {}

        if not subcategory:
            subcategory = 'No subcategory'

        if not subcategory in expenses[category]:
            expenses[category][subcategory] = {}


        if not date in expenses[category][subcategory]:
            expenses[category][subcategory][date] = abs(transaction.value)
        else:
            expenses[category][subcategory][date] = expenses[category][subcategory][date] + \
                abs(transaction.value)


    # Fill empty categories
    timeline = get_timeline(transactions)
    for category, category_expenses in expenses.items():
        for subcategory, subcategory_expenses in category_expenses.items():
            for date in timeline:
                if not date in subcategory_expenses:
                    subcategory_expenses[date] = 0


    for category, category_expenses in expenses.items():
        for subcategory, subcategory_expenses in category_expenses.items():
            subcategory_expenses = dict(sorted(subcategory_expenses.items()))

    return expenses


def get_year_expenses_by_category_with_subcategory(transactions: list[Transaction]):
    """
    Return a dict with the sum of all expenses for each categories and at the same time the same
    information for each subcategory.
    """
    expenses = {}
    for transaction in reversed(transactions):

        if transaction.transaction_type != 'EXPENSE':
            continue

        date = transaction.date.year
        category = transaction.category
        subcategory = transaction.subcategory
        value = abs(transaction.value)

        # Sum of all
        if "sum" not in expenses:
            expenses['sum'] = value
        else:
            expenses['sum'] = expenses['sum'] + value


        # Global expenses
        if "year" not in expenses:
            expenses['year'] = {}

        if date not in expenses['year']:
            expenses['year'][date] = value
        else:
            expenses['year'][date] = expenses['year'][date] + value


        # Categories
        if "categories" not in expenses:
            expenses['categories']= {}

        if category not in expenses['categories']:
            expenses['categories'][category] = {}
            expenses['categories'][category]['sum'] = value
            expenses['categories'][category]['year'] = {}
        else:
            expenses['categories'][category]['sum'] = value + \
            expenses['categories'][category]['sum']

        if date not in expenses['categories'][category]['year']:
            expenses['categories'][category]['year'][date] =  value
        else:
            expenses['categories'][category]['year'][date] =  value + \
                expenses['categories'][category]['year'][date]


        # Subcategories
        if "subcategories" not in expenses['categories'][category]:
            expenses['categories'][category]['subcategories']= {}


        if subcategory is None or subcategory == '':
            continue

        if not subcategory in expenses['categories'][category]['subcategories']:
            expenses['categories'][category]['subcategories'][subcategory] = {}
            expenses['categories'][category]['subcategories'][subcategory]['sum'] = value
            expenses['categories'][category]['subcategories'][subcategory]['year'] = {}
        else:
            expenses['categories'][category]['subcategories'][subcategory]['sum'] = value + \
                expenses['categories'][category]['subcategories'][subcategory]['sum']

        if not date in expenses['categories'][category]['subcategories'][subcategory]['year']:
            expenses['categories'][category]['subcategories'][subcategory]['year'][date] =  value
        else:
            expenses['categories'][category]['subcategories'][subcategory]['year'][date] =  value +\
                expenses['categories'][category]['subcategories'][subcategory]['year'][date]

    return expenses


def _get_number_of_months_with_transactions_in_year(transactions, year):
    """"
    Return the number of months with transactions by checking the last month and the first one
    """
    min_date: datetime = _get_min_date(transactions)
    max_date: datetime = _get_max_date(transactions)

    if year == min_date.year:
        return 13 - int(min_date.month)
    if year == max_date.year:
        return int(max_date.month)

    return 12


def get_expenses_years(transactions) ->list:
    """
    Return the years where there are transactions
    """
    min_date: datetime = _get_min_date(transactions)
    max_date: datetime = _get_max_date(transactions)

    return list(range(min_date.year, max_date.year+1, 1))


def get_avg_category_expense_per_month_in_year(transactions):
    """
    Return the average expenses per category and subcategory per year
    """
    year_expenses = get_year_expenses_by_category_with_subcategory(transactions)['categories']

    avg_expenses = {}
    for category, cat_expenses in year_expenses.items():
        avg_expenses[category] = {'year': {}, 'subcategories': {}} # Initialize
        for year, year_expense in cat_expenses['year'].items():
            avg_expenses[category]['year'][year] = \
                year_expense / _get_number_of_months_with_transactions_in_year(transactions, year)
        for subcategory, subcat_expenses in cat_expenses['subcategories'].items():
            avg_expenses[category]['subcategories'][subcategory] = {'year': {}}
            for subcat_year, subcat_year_expense in subcat_expenses['year'].items():
                avg_expenses[category]['subcategories'][subcategory]['year'][subcat_year] = \
                    subcat_year_expense / \
                        _get_number_of_months_with_transactions_in_year(transactions, subcat_year)

    return avg_expenses


def get_category_average_expenses(transactions):
    """
    Return a dict with the average transactions per year
    """
    expenses = get_avg_category_expense_per_month_in_year(transactions)
    years = get_expenses_years(transactions)
    
    avg_expenses = {}
    for category, category_expenses in expenses.items():
        
        # Fill empty years
        for year in years:
            if year not in category_expenses['year']:
                category_expenses['year'][year] = 0

        avg_expenses[category] = OrderedDict(
            sorted(category_expenses['year'].items(), reverse=False)
        )

    avg_expenses = OrderedDict(
        sorted(avg_expenses.items(), key=lambda x: sum(x[1].values()), reverse=True)
        )

    return avg_expenses
