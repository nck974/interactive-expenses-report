"""
Pydantic model fo the transactions
"""
# Disable no-self due to the validators of pydantic
# pylint: disable=no-self-argument
# pylint: disable=no-self-use
import csv
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator

class Transaction(BaseModel):
    """
    Representation of a transaction
    """
    date: datetime = Field(alias='Date')
    description: str = Field(alias='Description')
    value: float = Field(alias='Value')
    category: str = Field(alias='Category')
    tags: str  = Field(alias='Tags', default=None)
    account: str = Field(alias='Account', default=None)
    wallet: str = Field(alias='Wallet', default=None)
    subcategory: str = Field(alias='Subcategory', default=None)

    transaction_type: Optional[str]

    @validator("transaction_type", always=True)
    def validate_date(cls, _value, values):
        """
        Set a transaction type depending on the amount of the value
        """
        if values["value"] < 0:
            return "EXPENSE"
        return "INCOME"

    @validator("date", pre=True)
    def parse_date(cls, value):
        """
        Convert dates to datetime objects
        """
        return datetime.strptime(
            value,
            "%d/%m/%Y"
        )

    class Config:
        """
        Pydantic config
        """
        orm_mode = True


def _remove_duplicated_transactions(transactions: list[Transaction]):
    """
    Remove duplicated transactions to be safe from overlapping exports. Is considered a duplicated
    transaction when the  date, value, category and description match.
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
            print(f'The following duplicate has been removed:\n -> "{unique}"')

    return unique_list


def read_transactions(csv_files) -> list[Transaction]:
    """
    Read all transactions from a csv file and return them as a list of the pydantic model.
    """
    transactions = []
    for csv_file in csv_files:
        with open(csv_file, mode='r',  encoding='utf-16') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                transactions.append( Transaction(**row) )

    if not transactions:
        raise ValueError('No transactions could be found in the CSV file')

    transactions = _remove_duplicated_transactions(transactions)

    return transactions
