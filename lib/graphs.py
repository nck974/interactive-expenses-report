"""
Generate some graphs making use of plotly
"""

from dataclasses import dataclass
from plotly.offline import plot
import plotly.graph_objects as go
from lib.transaction import Transaction

from lib.stats import (
    get_categories_average_in_year,
    get_balance,
    get_balance_percentage,
    get_categories_average_in_year_with_subcategories,
    get_metric_average,
    get_categories_by_month,
    get_categories_by_month_with_subcategories,
    get_transactions_by_month,
)


class GraphTemplate:
    """
    Template to generate a graph which includes the methods to export an HTML to be used in the
    HTML report
    """

    transactions: list[Transaction]
    fig: go.Figure

    def __init__(self, transactions: list[Transaction] = None) -> None:
        self.transactions = transactions
        self.fig = go.Figure()
        self.fig.update_layout(template=self._get_default_theme_template())

    def plot(self):
        """
        Plot the graph to check it live
        """
        self.fig.show()

    def get_html(self):
        """
        Return graph as html code
        """
        return plot(
            self.fig,
            output_type="div",
            show_link=False,
            include_plotlyjs=False,
            image_height=800,
        )

    @classmethod
    def _smooth_curve(cls, scalars: list[float], weight: float) -> list[float]:
        """
        Smooth a curve by creating the same amount of values but smoothned to mitigate sharp points
        outside the tendency of the graph
        weight: Weight between 0 and 1
        """
        last = scalars[0]  # First value in the plot (first timestep)
        smoothed = []
        for point in scalars:
            smoothed_val = (
                last * weight + (1 - weight) * point
            )  # Calculate smoothed value
            smoothed.append(smoothed_val)  # Save it
            last = smoothed_val  # Anchor the last smoothed value

        return smoothed

    @classmethod
    def _get_default_theme_template(cls):
        """
        Return the default templates to create a theme for the graphs
        """
        return "plotly_dark"


class IncomeExpenses(GraphTemplate):
    """
    Plot the expenses divided by main categories in an area stacked plot
    """

    def __init__(self, transactions):
        super().__init__(transactions)
        self._create_plot()

    def _create_plot(self):
        """
        Create income/expenses subplot
        """
        expenses = get_transactions_by_month(self.transactions, "EXPENSE")
        income = get_transactions_by_month(self.transactions, "INCOME")

        # EXPENSES
        self.fig.add_trace(
            go.Scatter(
                name="Expenses",
                marker_color="red",
                x=list(expenses.keys()),
                y=list(expenses.values()),
            ),
        )

        # Expenses trend
        expenses_trend = self._smooth_curve(list(expenses.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(
                name="Expenses smoothed",
                mode="lines",
                x=list(expenses.keys()),
                y=expenses_trend,
                marker_color="red",
                opacity=0.3,
            ),
        )

        # INCOME
        self.fig.add_trace(
            go.Scatter(
                name="Income",
                marker_color="green",
                x=list(income.keys()),
                y=list(income.values()),
            )
        )

        # Income trend
        income_trend = self._smooth_curve(list(income.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(
                name="Income smoothed",
                mode="lines",
                x=list(income.keys()),
                y=income_trend,
                marker_color="green",
                opacity=0.3,
            ),
        )

        # Axis
        self.fig.update_yaxes(showticksuffix="all", ticksuffix="€")


class Balance(GraphTemplate):
    """
    Plot the balance of the income/expenses
    """

    def __init__(self, transactions):
        super().__init__(transactions)
        self._create_plot()

    def _create_plot(self):
        """
        Create balance subplot
        """
        balance = get_balance(self.transactions)

        # BALANCE
        self.fig.add_trace(
            go.Scatter(
                name="Balance",
                mode="lines+markers",
                x=list(balance.keys()),
                y=list(balance.values()),
                marker_color=list(map(self.__set_color, list(balance.values()))),
                line_color="orange",
            ),
        )

        # Balance trend
        balance_trend = self._smooth_curve(list(balance.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(
                name="Balance smoothed",
                mode="lines",
                x=list(balance.keys()),
                y=balance_trend,
                marker_color="orange",
                opacity=0.3,
            ),
        )
        self.fig.update_yaxes(showticksuffix="all", ticksuffix="€")

    @classmethod
    def __set_color(cls, value) -> str:
        """
        Set color base on the values
        """
        if value <= 0:
            return "red"

        return "green"


class RelativeBalance(GraphTemplate):
    """
    Plot the balance of the income to expenses as a percent
    """

    def __init__(self, transactions):
        super().__init__(transactions)
        self._create_plot()

    def _create_plot(self):
        """
        Create relative balance plot
        """
        balance = get_balance_percentage(self.transactions)

        # BALANCE %
        self.fig.add_trace(
            go.Scatter(
                name="Balance",
                mode="lines+markers",
                x=list(balance.keys()),
                y=list(balance.values()),
                marker_color=list(map(self.__set_color, list(balance.values()))),
                marker_size=7,
                line_color="orange",
            ),
        )
        balance_percentage_trend = self._smooth_curve(list(balance.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(
                x=list(balance.keys()),
                y=balance_percentage_trend,
                mode="lines",
                name="Balance smoothed",
                marker_color="goldenrod",
                opacity=0.5,
            ),
        )

        # Mark average saving
        balance_avg = get_metric_average(balance)
        if balance_avg is not None:
            self.fig.add_hline(
                y=balance_avg,
                line_dash="dash",
                line_color="yellow",
                annotation_text=f"Average ({balance_avg:.2f}%)",
                annotation_position="bottom right",
            )
        # Mark 0
        self.fig.add_hline(
            y=0,
            line_color="red",
        )

        # Axis
        self.fig.update_yaxes(range=[-50, 75], showticksuffix="all", ticksuffix="%")

    @classmethod
    def __set_color(cls, value) -> str:
        """
        Set color base on the values
        """
        if value <= 0:
            return "red"

        return "green"


class CategoriesMonthArea(GraphTemplate):
    """
    Plot the expenses divided by main categories in an area stacked plot
    """

    def __init__(self, transactions):
        super().__init__(transactions)
        self._create_plot()

    def _create_plot(self):
        """
        Create a plot with all categories stacked in bars sorted by expenses amount.
        This graph does not distinguish between subcategories.
        """
        expenses = get_categories_by_month(self.transactions, "EXPENSE")

        for category, category_expenses in expenses.items():
            self.fig.add_trace(
                go.Scatter(
                    name=category,
                    x=list(category_expenses.keys()),
                    y=list(category_expenses.values()),
                    stackgroup="one",
                    mode="lines",
                )
            )


class CategoriesMonthBars(GraphTemplate):
    """
    Plot the expenses divided by main categories
    """

    def __init__(self, transactions: list[Transaction]):
        super().__init__(transactions)
        self._create_plot()

    def _create_plot(self):
        """
        Create a subplot with all categories stacked in bars sorted by expenses amount
        This graph does not distinguish between subcategories.
        """
        expenses = get_categories_by_month(self.transactions, "EXPENSE")

        for category, category_expenses in expenses.items():
            self.fig.add_trace(
                go.Bar(
                    name=category,
                    x=list(category_expenses.keys()),
                    y=list(category_expenses.values()),
                )
            )

        self.fig.update_layout(barmode="stack")

        # Axis
        self.fig.update_yaxes(showticksuffix="all", ticksuffix="€")


class CategoriesAverageYear(GraphTemplate):
    """
    Plot the average expenses by category per year
    """

    def __init__(self, transactions: list[Transaction]):
        super().__init__(transactions)
        self._create_plot()

    def _create_plot(self):
        """
        Create a plot with all average expenses per category
        """
        expenses = get_categories_average_in_year(self.transactions)

        for category, category_expenses in expenses.items():
            self.fig.add_trace(
                go.Bar(
                    name=category,
                    x=list(category_expenses.keys()),
                    y=list(category_expenses.values()),
                )
            )

        self.fig.update_layout(barmode="stack")

        # Axis
        self.fig.update_yaxes(showticksuffix="all", ticksuffix="€")


class CategoryDetail(GraphTemplate):
    """
    Plot the expenses of a category in a bar graph as the sum of all subcategories for each
    available month
    """

    def __init__(
        self,
        transactions,
        category: str,
        subcategories: dict[str : dict[str : int | float]],
    ):
        super().__init__(transactions=transactions)
        self.subcategories = subcategories
        self.category = category
        self._create_plot()

    def _create_plot(self) -> None:
        """
        Create a subplot with all sub categories stacked in bars.
        """
        for subcategory, subcategory_expenses in self.subcategories.items():
            self.fig.add_trace(
                go.Bar(
                    name=subcategory,
                    x=list(subcategory_expenses.keys()),
                    y=list(subcategory_expenses.values()),
                )
            )

        self.fig.update_layout(barmode="stack")

        # Average
        category_expenses = get_categories_by_month(self.transactions, "EXPENSE")[
            self.category
        ]
        category_avg = get_metric_average(category_expenses)
        self.fig.add_hline(
            y=category_avg,
            line_dash="dash",
            annotation_text=f"Average: ({category_avg:.2f}€)",
            annotation_position="bottom right",
        )

        # Axis
        self.fig.update_yaxes(showticksuffix="all", ticksuffix="€")


class CategoryYearAvg(GraphTemplate):
    """
    Plot the average of subcategories in a bar graph per month per year
    """

    def __init__(
        self,
        transactions,
        category: str,
        subcategories: dict[str : dict[str : int | float]],
    ):
        super().__init__(transactions=transactions)
        self.subcategories = subcategories
        self.category = category
        self._create_plot()

    def _create_plot(self):
        """
        Create a subplot with all sub categories stacked in bars.
        """
        for subcategory, subcategory_expenses in self.subcategories.items():
            self.fig.add_trace(
                go.Bar(
                    name=subcategory,
                    x=list(subcategory_expenses["year"].keys()),
                    y=list(subcategory_expenses["year"].values()),
                )
            )

        self.fig.update_layout(barmode="stack")

        # Axis
        self.fig.update_yaxes(showticksuffix="all", ticksuffix="€")


@dataclass
class HTMLGraph:
    """
    Dataclass of a graph that will be represented in the HTML
    """

    name: str
    html: str


def get_overview_graphs(transactions: list[Transaction]) -> list[HTMLGraph]:
    """
    Generate the graphs that summarize the balance and expenses
    """
    graph_list = {
        "Income & expenses": IncomeExpenses,
        "Balance": Balance,
        "Relative balance": RelativeBalance,
        "Expenses per category (stacked area)": CategoriesMonthArea,
        "Expenses per category (bars)": CategoriesMonthBars,
        "Category average monthly expense per year": CategoriesAverageYear,
    }

    overview_graphs = []
    for name, graph in graph_list.items():
        overview_graphs.append(
            HTMLGraph(name=name, html=graph(transactions=transactions).get_html())
        )
    return overview_graphs


def get_category_detailed_bar_graphs(
    transactions: list[Transaction],
) -> list[HTMLGraph]:
    """
    Return a list of graphs with the details of each category for each month
    """
    expenses = get_categories_by_month_with_subcategories(transactions, "EXPENSE")
    graphs = []
    for category, cat_expenses in expenses.items():
        cat_details = CategoryDetail(transactions, category, cat_expenses)
        graphs.append(HTMLGraph(name=category, html=cat_details.get_html()))
    return graphs


def get_category_average_bar_graphs(transactions: list[Transaction]) -> list[HTMLGraph]:
    """
    Return a dict of graphs with all categories divided in subcategories. Structure:

    """
    expenses = get_categories_average_in_year_with_subcategories(transactions)

    graphs: list[HTMLGraph] = []
    for category, cat_expenses in expenses.items():
        cat_details = CategoryYearAvg(
            transactions, category, cat_expenses["subcategories"]
        )
        graphs.append(HTMLGraph(name=category, html=cat_details.get_html()))
    return graphs
