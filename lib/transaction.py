"""
Pydantic model fo the transactions
"""
# Disable no-self due to the validators of pydantic
# pylint: disable=no-self-argument
# pylint: disable=no-self-use
import csv
import re
from typing import Any, Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator  # type: ignore


def _fix_utf8_characters(string: str) -> str:
    """
    Remove icons not supported by ansi
    """
    string = re.sub(re.escape("??"), "", string)
    string = re.sub(re.escape("?"), "", string)
    return string.strip()


class Transaction(BaseModel):
    """
    Representation of a transaction
    """

    date: datetime = Field(alias="Date")
    description: str = Field(alias="Note")
    category: str = Field(alias="Category")
    value: float = Field(alias="Amount")
    tags: str = Field(alias="Tags", default=None)
    account: str = Field(alias="Account", default=None)
    wallet: str = Field(alias="Wallet", default=None)
    subcategory: str = Field(alias="Subcategory", default=None)

    transaction_type: Optional[str] = Field(default=None, alias="Income/Expense")

    @validator("transaction_type", always=True, pre=True)
    def validate_type(cls, value: Any):
        """
        Set a transaction type depending on the amount of the value
        """
        if value == "Expense":
            return "EXPENSE"
        return "INCOME"

    @validator("date", pre=True)
    def parse_date(cls, value: Any):
        """
        Convert dates to datetime objects
        """
        if value is not None:
            return datetime.strptime(value, "%m/%d/%Y")
        return value

    @validator(*["subcategory", "category"], pre=True)
    def fix_utf8(cls, value: Any):
        """
        Fix utf8 characters
        """
        if value is not None:
            return _fix_utf8_characters(value)
        return value

    class Config:
        """
        Pydantic config
        """

        orm_mode = True


def _remove_duplicated_transactions(
    transactions: list[Transaction],
) -> list[Transaction]:
    """
    Remove duplicated transactions to be safe from overlapping exports. Is considered a duplicated
    transaction when the  date, value, category and description match.
    """
    seen_transactions: set[str] = set()
    unique_list: list[Transaction] = []
    for transaction in transactions:
        unique = (
            f"{transaction.date.isoformat()}-{transaction.description}"
            + f"-{transaction.value}-{transaction.description}"
        )
        if unique not in seen_transactions:
            unique_list.append(transaction)
            seen_transactions.add(unique)
        else:
            print(f'The following duplicate has been removed:\n -> "{unique}"')

    return unique_list


def read_transactions(csv_files: list[str]) -> list[Transaction]:
    """
    Read all transactions from a csv file and return them as a list of the pydantic model.
    """
    transactions: list[Transaction] = []
    for csv_file in csv_files:
        with open(csv_file, mode="r", encoding="ANSI") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for row in reader:
                transactions.append(Transaction(**row))  # type: ignore

    if not transactions:
        raise ValueError("No transactions could be found in the CSV file")

    transactions = _remove_duplicated_transactions(transactions)

    return transactions
