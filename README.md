[![Pylint](https://github.com/nck974/interactive-expenses-report/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/nck974/interactive-expenses-report/actions/workflows/pylint.yml)
[![CodeQL](https://github.com/nck974/interactive-expenses-report/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/nck974/interactive-expenses-report/actions/workflows/codeql-analysis.yml)

# Interactive Expenses Report

Create an HTML report of your expenses from a set of expenses/income stored in a CSV file. The expected structure is the default export of the app [`Money Manager`]. Although the app is good at tracking expenses as it can be done quickly at any time, I don't like the data visualization or is not helpful enough.

This project aims to create some graphs from that data which can give you a better overview where are you spending your money.

The goal is to have a single file self contained which has enough information to make some decisions.

<p align="center">
  <img src="static/images/example.gif" width="800px" alt="Example">
</p>

A complete report example can be found in the `example` folder.

## Data structure

The expected input has to be stored as a `.csv` file inside the `input folder` with the following format:

```shell
"Date";"Description";"Value";"Account";"Category";"Subcategory";"Tags"
"dd/mm/yyyy";"My expense name";"-xxx.xx";"Wallet";"category name";"subcategory name";" (currently not used)"
"dd/mm/yyyy";"My income name";"xxx.xx";"Wallet";"category name";"subcategory name";" (currently not used)"
```

Note that the differentiation between of incomes and expenses is only done by the sign of the value. `Date`, `Note`, `Amount`, `Income/Expense`, and `Category` are mandatory fields.

- *Date*: Date. Date in the format `%m/%d/%Y`.
- *Amount*: Float.
- *Income/Expense*: Possible values `EXPENSE` or `INCOME`.
- *Account*: Not used.
- *Tags*: Not used.
- *Description*: Ma,e pf the transaction.
- *category*: String. Name of the category of an income/expense.
- *subcategory*: String Name of the subcategory of an income/expense within a category. Not mandatory.

## Prerequisites

### No docker

- `python 3.10` should be installed, although `3.9` may work it has not been tested.

### Docker

- Docker is installed.

## Installation

### No Docker

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

### Docker installation

- No installation is required.

## Usage

### Docker usage

1. You can make use of the `docker-compose.yaml` provided.
1. Place your expenses `.csv` files in the `input` folder.
1. Start the docker compose with `docker-compose up`.
1. The report shall be generated in the `output` folder.

### No docker usage

1. Install the dependencies with `pip install -r requirements.txt`
1. Place the expenses csv files inside the `input` folder.
1. Execute the `interactive_expenses_report.py` script with:

    ```shell
    python .\interactive_expenses_report.py
    ```

1. The report will appear generated with the current date in the `output` folder.

## Settings

The settings that could be changed like `currency` or the `report title` can be changed in the `settings.py` file. This is currently only supported in the non docker mode.

## Development

1. Create docker images:
    1. Build the docker image with

        ```shell
        docker build --tag interactive-expenses-report:x.y.z .
        ```

    1. Create the tags:

        ```shell
        docker tag interactive-expenses-report:x.y.z nck974/interactive-expenses-report:xyz
        docker tag interactive-expenses-report:x.y.z nck974/interactive-expenses-report:latest
        ```

    1. Push the images to the registry:

        ```shell
        docker push nck974/interactive-expenses-report:x.y.z
        docker push nck974/interactive-expenses-report:latest
        ```

## Support

This project took more than `13h` (measured thanks to [wakapi](https://github.com/muety/wakapi)) at a rate of around 1 coffee each 2h. If this is useful [consider donating one coffee](https://www.buymeacoffee.com/nck974), adding a start or proposing features.  
<p align="center">
  <img src="static/images/support.png" width="800px">
</p>
