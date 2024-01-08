"""
This file takes charge of grouping and sorting all transactions to be plotted
"""
from collections import OrderedDict
from datetime import datetime
from typing import Any

from lib.transaction import Transaction


def _get_min_date(transactions: list[Transaction]) -> datetime | None:
    """
    Return the date of the oldest transaction
    """
    min_date: datetime | None = None
    for transaction in transactions:
        if min_date is None:
            min_date = transaction.date
        else:
            if min_date > transaction.date:
                min_date = transaction.date
    return min_date


def _get_max_date(transactions: list[Transaction]) -> datetime | None:
    """
    Return the date of the oldest transaction
    """
    max_date: datetime | None = None
    for transaction in transactions:
        if max_date is None:
            max_date = transaction.date
        else:
            if max_date < transaction.date:
                max_date = transaction.date
    return max_date


def get_months(transactions: list[Transaction]) -> list[str]:
    """
    Return a list of strings for each month of each year available in the transactions
    """
    min_date = _get_min_date(transactions)
    max_date = _get_max_date(transactions)

    if min_date is None or max_date is None:
        raise RuntimeError("Dates could not be found")

    months: list[str] = []
    for year in range(min_date.year, max_date.year + 1):
        for month in range(1, 12 + 1):
            if year == min_date.year and month < min_date.month:
                continue
            if year == max_date.year and month > max_date.month:
                continue
            month_number = datetime(1900, month, 1).strftime("%m")
            months.append(f"{str(year)[-2:]}_{month_number}")

    return months


def get_transactions_by_month(
    raw_transactions: list[Transaction], trans_type: str
) -> dict[str, float]:
    """
    Get the total expenses by month of the given list of transactions
    trans_type: Can be the string 'EXPENSE' or 'INCOME'
    """
    transactions: dict[str, float] = {}
    for transaction in raw_transactions:
        if transaction.transaction_type != trans_type:
            continue

        date = f'{str(transaction.date.year)[-2:]}_{transaction.date.strftime("%m")}'
        if date in transactions:
            transactions[date] = transactions[date] + abs(transaction.value)
        else:
            transactions[date] = abs(transaction.value)

    # Set to 0 all months that are not present
    months = get_months(raw_transactions)
    for month in months:
        if not month in transactions:
            transactions[month] = 0

    transactions = dict(sorted(transactions.items()))

    return transactions


def get_balance(transactions: list[Transaction]) -> dict[str, float]:
    """
    Get difference between expenses and income per month
    """
    expenses = get_transactions_by_month(transactions, "EXPENSE")
    income = get_transactions_by_month(transactions, "INCOME")
    balance: dict[str, float] = {}
    for date, expense in expenses.items():
        income_value = income[date]
        balance[date] = income_value - abs(expense)
    return balance


def get_balance_percentage(transactions: list[Transaction]) -> dict[str, float]:
    """
    Get difference between expenses and income per month as a percentage
    """
    expenses = get_transactions_by_month(transactions, "EXPENSE")
    income = get_transactions_by_month(transactions, "INCOME")
    balance: dict[str, float] = {}
    for date, expense in expenses.items():
        income_value = income[date]
        if income_value == 0:
            balance[date] = 0
        else:
            balance[date] = (income_value - abs(expense)) / income_value * 100
    return balance


def get_metric_average(metrics: dict[str, float]) -> float | int:
    """
    Metric average
    """
    total = 0
    count = 0
    for metric in metrics.values():
        total = total + metric
        count = count + 1
    return total / count


def _sort_categories_by_expense(expenses: dict[str, Any]) -> list[str]:
    """
    Sort the categories from the one with more expenses to the least
    See: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    """
    category_total_expenses: dict[str, float] = {}
    for category in expenses.keys():
        for date in expenses[category]:
            if category in category_total_expenses:
                category_total_expenses[category] = (
                    category_total_expenses[category] + expenses[category][date]
                )
            else:
                category_total_expenses[category] = expenses[category][date]
    category_total_expenses = OrderedDict(
        sorted(category_total_expenses.items(), key=lambda x: x[1], reverse=True)
    )
    return list(map(str, category_total_expenses.keys()))


def get_categories_by_month(
    transactions: list[Transaction], trans_type: str
) -> OrderedDict[str, dict[str, float]]:
    """
    Return a dict with the list of categories (without subcategories)
    trans_type: Can be 'EXPENSE' or 'INCOME'
    """
    expenses = {}
    for transaction in transactions:
        if transaction.transaction_type != trans_type:
            continue

        date = f'{str(transaction.date.year)[-2:]}_{transaction.date.strftime("%m")}'
        category = transaction.category

        if category not in expenses:
            expenses[category] = {}

        if date not in expenses[category]:
            expenses[category][date] = abs(transaction.value)
        else:
            expenses[category][date] = expenses[category][date] + abs(transaction.value)

    # Fill empty categories
    months = get_months(transactions)
    for category, cat_expenses in expenses.items():
        for month in months:
            if not month in cat_expenses:
                cat_expenses[month] = 0

    # Sort by total amount spent
    sorted_categories = _sort_categories_by_expense(expenses)

    # Sort dates
    category_expenses = OrderedDict()
    for category in sorted_categories:
        category_expenses[category] = dict(sorted(expenses[category].items()))

    return category_expenses


def get_categories_by_month_with_subcategories(
    transactions: list[Transaction], trans_type: str
) -> dict:
    """
    Get monthly expenses with the details of the subcategories.
    If an expense does not have a subcategory a default 'No subcategory' will be created.
    trans_type: Can be 'EXPENSE' or 'INCOME'
    """

    def _fill_empty_subcategories(expenses):
        """
        Fill with a 0 all months that are empty
        """
        # Fill empty categories
        months = get_months(transactions)
        for category, category_expenses in expenses.items():
            for subcategory, subcategory_expenses in category_expenses.items():
                for month in months:
                    if not month in subcategory_expenses:
                        expenses[category][subcategory][month] = 0
        return expenses

    def _sort_categories(expenses):
        """
        Sort the categories by sum of expenses and sort the dates chronologically
        """
        for category, category_expenses in expenses.items():
            for subcategory, subcategory_expenses in category_expenses.items():
                expenses[category][subcategory] = dict(
                    sorted(subcategory_expenses.items())
                )

            # Sort from more expenses to less the subcategories
            expenses[category] = OrderedDict(
                sorted(
                    expenses[category].items(),
                    key=lambda x: sum(x[1].values()),
                    reverse=True,
                )
            )
        return expenses

    expenses = {}
    for transaction in transactions:
        if transaction.transaction_type != trans_type:
            continue

        date = f'{str(transaction.date.year)[-2:]}_{transaction.date.strftime("%m")}'
        category = transaction.category
        subcategory = transaction.subcategory

        if not category in expenses:
            expenses[category] = {}

        if not subcategory:
            subcategory = "No subcategory"

        if not subcategory in expenses[category]:
            expenses[category][subcategory] = {}

        if not date in expenses[category][subcategory]:
            expenses[category][subcategory][date] = abs(transaction.value)
        else:
            expenses[category][subcategory][date] = expenses[category][subcategory][
                date
            ] + abs(transaction.value)

    expenses = _fill_empty_subcategories(expenses)
    expenses = _sort_categories(expenses)

    return expenses


def get_categories_by_year_with_subcategory(
    transactions: list[Transaction],
) -> dict[str, Any]:
    """
    Return a dict with the sum of all expenses for each categories and at the same time the same
    information for each subcategory.
    Example:
    \\_ sum
    \\_ year
        \\_2022: 200
    \\_categories
        \\_<category_name>
            \\_ sum
            \\_ year
                \\_2022: 200
            \\_subcategories
                \\<subcategory_name>
                    \\_ sum
                    \\_ year
                        \\_2022: 200
    """

    def _fill_global_expenses(expenses, date, value):
        """
        Fill the summary of all years and expenses
        """
        # Sum of all
        if "sum" not in expenses:
            expenses["sum"] = value
        else:
            expenses["sum"] = expenses["sum"] + value

        # Global expenses
        if "year" not in expenses:
            expenses["year"] = {}

        if date not in expenses["year"]:
            expenses["year"][date] = value
        else:
            expenses["year"][date] = expenses["year"][date] + value
        return expenses

    def _fill_category(expenses, category, date, value):
        """
        Fill the category in the structure
        """
        if "categories" not in expenses:
            expenses["categories"] = {}

        if category not in expenses["categories"]:
            expenses["categories"][category] = {}
            expenses["categories"][category]["sum"] = value
            expenses["categories"][category]["year"] = {}
        else:
            expenses["categories"][category]["sum"] = (
                value + expenses["categories"][category]["sum"]
            )

        if date not in expenses["categories"][category]["year"]:
            expenses["categories"][category]["year"][date] = value
        else:
            expenses["categories"][category]["year"][date] = (
                value + expenses["categories"][category]["year"][date]
            )

        return expenses

    def _fill_subcategory(expenses, category, subcategory, date, value):
        """
        Fill the subcategory in the structure within a category
        """
        if "subcategories" not in expenses["categories"][category]:
            expenses["categories"][category]["subcategories"] = {}

        if subcategory is None or subcategory == "":
            subcategory = "No subcategory"

        if not subcategory in expenses["categories"][category]["subcategories"]:
            expenses["categories"][category]["subcategories"][subcategory] = {}
            expenses["categories"][category]["subcategories"][subcategory][
                "sum"
            ] = value
            expenses["categories"][category]["subcategories"][subcategory]["year"] = {}
        else:
            expenses["categories"][category]["subcategories"][subcategory]["sum"] = (
                value
                + expenses["categories"][category]["subcategories"][subcategory]["sum"]
            )

        if (
            not date
            in expenses["categories"][category]["subcategories"][subcategory]["year"]
        ):
            expenses["categories"][category]["subcategories"][subcategory]["year"][
                date
            ] = value
        else:
            expenses["categories"][category]["subcategories"][subcategory]["year"][
                date
            ] = (
                value
                + expenses["categories"][category]["subcategories"][subcategory][
                    "year"
                ][date]
            )

        return expenses

    expenses = {}
    for transaction in reversed(transactions):
        if transaction.transaction_type != "EXPENSE":
            continue

        date = transaction.date.year
        category = transaction.category
        subcategory = transaction.subcategory
        value = abs(transaction.value)

        expenses = _fill_global_expenses(expenses, date, value)
        expenses = _fill_category(expenses, category, date, value)
        expenses = _fill_subcategory(expenses, category, subcategory, date, value)

    return expenses


def _get_number_of_months_with_transactions_in_year(transactions, year):
    """ "
    Return the number of months with transactions by checking the last month and the first one
    This is used to calculate the average expenses of a year which has not finished
    """
    min_date: datetime = _get_min_date(transactions)
    max_date: datetime = _get_max_date(transactions)

    if year == min_date.year:
        return 13 - int(min_date.month)
    if year == max_date.year:
        return int(max_date.month)

    return 12


def get_years(transactions) -> list:
    """
    Return the years where there are transactions
    """
    min_date: datetime = _get_min_date(transactions)
    max_date: datetime = _get_max_date(transactions)

    return list(range(min_date.year, max_date.year + 1, 1))


def get_categories_average_in_year_with_subcategories(transactions):
    """
    Return the average expenses per category and subcategory per year
    """
    year_expenses = get_categories_by_year_with_subcategory(transactions)["categories"]
    years = get_years(transactions)

    avg_expenses = {}
    for category, cat_expenses in year_expenses.items():
        avg_expenses[category] = {"year": {}, "subcategories": {}}  # Initialize

        if not "year" in cat_expenses:
            cat_expenses["year"] = {}

        for year in years:
            if year in cat_expenses["year"]:
                avg_expenses[category]["year"][year] = cat_expenses["year"][
                    year
                ] / _get_number_of_months_with_transactions_in_year(transactions, year)
            else:
                avg_expenses[category]["year"][year] = 0

        for subcategory, subcat_expenses in cat_expenses["subcategories"].items():
            avg_expenses[category]["subcategories"][subcategory] = {"year": {}}

            for subyear in years:
                if subyear in subcat_expenses["year"]:
                    avg_expenses[category]["subcategories"][subcategory]["year"][
                        subyear
                    ] = subcat_expenses["year"][
                        subyear
                    ] / _get_number_of_months_with_transactions_in_year(
                        transactions, subyear
                    )
                else:
                    avg_expenses[category]["subcategories"][subcategory]["year"][
                        subyear
                    ] = 0

    return avg_expenses


def get_categories_average_in_year(transactions):
    """
    Return a dict with the average transactions per year
    """
    expenses = get_categories_average_in_year_with_subcategories(transactions)
    years = get_years(transactions)

    avg_expenses = {}
    for category, category_expenses in expenses.items():
        # Fill empty years
        for year in years:
            if year not in category_expenses["year"]:
                category_expenses["year"][year] = 0

        avg_expenses[category] = OrderedDict(
            sorted(category_expenses["year"].items(), reverse=False)
        )

    avg_expenses = OrderedDict(
        sorted(avg_expenses.items(), key=lambda x: sum(x[1].values()), reverse=True)
    )

    return avg_expenses
