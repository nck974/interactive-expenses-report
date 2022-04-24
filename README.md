[![Pylint](https://github.com/nck974/interactive-expenses-report/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/nck974/interactive-expenses-report/actions/workflows/pylint.yml)
# Interactive Expenses Report

Create an HTML report of your expenses from a set of expenses/income stored in a CSV file. The expected structure is the default export of the app [`Mobills`](https://www.mobillsapp.com/). Although the app is good at tracking expenses as it can be done quickly at any time, I don't like the data visualization or is not helpful enough.

This project aims to create some graphs from that data which can give you a better overview where are you spending your money.

<p align="center">
  <img src="static/images/index.png" width="500px">
  <img src="static/images/overview.png" width="500px">
  <img src="static/images/balance.png" width="500px">
  <img src="static/images/year.png" width="500px">
</p>

## Data structure

The expected input has to be stored as a `.csv` file inside the `input folder` with the following format:
```shell
"Date";"Description";"Value";"Account";"Category";"Subcategory";"Tags"
"dd/mm/yyyy";"My expense name";"-xxx.xx";"Wallet";"category name";"subcategory name";" (currently not used)"
"dd/mm/yyyy";"My income name";"xxx.xx";"Wallet";"category name";"subcategory name";" (currently not used)"
```

Note that the differentiation between of incomes and expenses is only done by the sign of the value. `Date`, `value`, `description`, and `category` are mandatory fields.

## Prerequisites

1. `python 3.10` should be installed, although `3.9` may work it has not been tested.

## Installation

1. Clone the project or download the last release.
1. Is recommended to use a virtual environment:
    ```shell
    pip install virtualenv
    python -m virtualenv .venv
    .\.venv\Scripts\activate
    ```
1. Install the python dependencies
    ```shell
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Usage

1. Place the expenses csv files inside the `input` folder.
1. Execute the `interactive_expenses_report.py` script with:
    ```shell
    python .\interactive_expenses_report.py
    ```
1. The report will appear generated with the current date in the `output` folder.


## Settings

The settings that could be changed like `currency` or the `report title` can be changed in the `settings.py` file.