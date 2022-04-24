"""
Pydantic model fo the transactions
"""
# Disable no-self due to the validators of pydantic
# pylint: disable=no-self-argument
# pylint: disable=no-self-use
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
