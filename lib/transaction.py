"""
Pydantic model fo the transactions
"""

# Disable no-self due to the validators of pydantic
# pylint: disable=no-self-argument
import csv
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    """
    Representation of a transaction
    """

    class Config:
        """
        Pydantic config
        """

        from_attributes = True

    date: datetime = Field(alias="Date")
    description: str = Field(alias="Note")
    category: str = Field(alias="Category")
    value: float = Field(alias="Amount")
    tags: Optional[str] = Field(alias="Tags", default=None)
    account: Optional[str] = Field(alias="Account", default=None)
    wallet: Optional[str] = Field(alias="Wallet", default=None)
    subcategory: Optional[str] = Field(alias="Subcategory", default=None)

    transaction_type: Optional[str] = Field(default=None, alias="Income/Expense")

    @field_validator("transaction_type", mode="before")
    def validate_type(cls, value: Any):
        """
        Set a transaction type depending on the amount of the value
        """
        if value == "Expense":
            return "EXPENSE"
        return "INCOME"

    @field_validator("date", mode="before")
    def parse_date(cls, value: Any):
        """
        Convert dates to datetime objects
        """
        try:
            return datetime.strptime(value, "%m/%d/%Y")
        except ValueError:
            return datetime.strptime(value, "%m/%d/%Y %H:%M:%S")


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
        with open(csv_file, mode="r", encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                transactions.append(Transaction(**row))  # type: ignore

    if not transactions:
        raise ValueError("No transactions could be found in the CSV file")

    transactions = _remove_duplicated_transactions(transactions)

    return transactions
