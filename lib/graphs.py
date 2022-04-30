"""
Generate some graphs making use of plotly
"""

from plotly.offline import plot
import plotly.graph_objects as go
from lib.transaction import Transaction

from lib.stats import (
    get_avg_category_expense_per_month_in_year,
    get_category_average_expenses,
    get_expenses_years,
    get_income_expenses_balance,
    get_inc_exp_balance_percent,
    get_metric_average,
    get_month_exp_by_category,
    get_month_exp_by_category_with_subcategories,
    get_monthly_total_expenses,
    get_monthly_total_income,
    get_timeline
)


class GraphTemplate():
    """
    Template to generate a graph which includes the methods to export an HTML to be used in the
    HTML report
    """
    transactions: list[Transaction]
    timeline: list[str]
    fig: go.Figure


    def __init__(self, transactions: list[Transaction]) -> None:
        self.transactions = transactions
        self.timeline = get_timeline(transactions)
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
            output_type='div',
            show_link=False,
            include_plotlyjs=False,
            image_height=800)

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
            smoothed_val = last * weight + (1 - weight) * point  # Calculate smoothed value
            smoothed.append(smoothed_val)                        # Save it
            last = smoothed_val                                  # Anchor the last smoothed value

        return smoothed

    @classmethod
    def _get_default_theme_template(cls):
        """
        Return the default templates to create a theme for the graphs
        """
        return 'plotly_dark'


class IncomeExpensesBalance(GraphTemplate):
    """
    Plot the balance of the income/expenses
    """

    def __init__(self, transactions):
        super().__init__(transactions)
        self.__create_plot()

    def __create_plot(self):
        """
        Create balance subplot
        """
        balance = get_income_expenses_balance(self.transactions)

        # BALANCE
        self.fig.add_trace(
            go.Scatter(
                mode="lines+markers",
                x=self.timeline, y=list(balance.values()), name="Balance",
                marker_color = list(map(self.__set_color, list(balance.values()))),
            ),
        )

        # Balance trend
        balance_trend = self._smooth_curve(list(balance.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(x=self.timeline, y=balance_trend, mode = "lines", name="Balance smoothed",
            marker_color = "orange", opacity=0.3),
        )
        self.fig.update_yaxes(showticksuffix='all', ticksuffix="€")

    @classmethod
    def __set_color(cls, value) -> str:
        """
        Set color base on the values
        """
        if value <= 0:
            return "red"

        return "green"



class IncomeExpensesRelativeBalance(GraphTemplate):
    """
    Plot the balance of the income/expenses
    """
    # DEFAULT_TARGET = 33.33

    def __init__(self, transactions):
        super().__init__(transactions)
        self.__create_plot()

    def __create_plot(self):
        """
        Create relative balance subplot
        """
        balance_percentage = get_inc_exp_balance_percent(self.transactions)
        balance_percentage_avg = get_metric_average(balance_percentage)

        # BALANCE %
        self.fig.add_trace(
            go.Scatter(
                mode="lines+markers",
                x=self.timeline, y=list(balance_percentage.values()),
                name="Balance",
                marker_color = list(map(self.__set_color, list(balance_percentage.values()))),
                marker_size=7,
            ),
        )
        balance_percentage_trend = self._smooth_curve(list(balance_percentage.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(
                x=self.timeline,
                y=balance_percentage_trend,
                mode = "lines", name="Balance smoothed",
            marker_color = "goldenrod", opacity=0.5),
        )

        # Mark average saving
        if balance_percentage_avg is not None:
            self.fig.add_hline(
                y=balance_percentage_avg, line_dash="dash", line_color="blue",
                annotation_text=f'Average saving ({balance_percentage_avg:.2f}%)',
                annotation_position="bottom right"
            )
        # Mark 0
        self.fig.add_hline(
                y=0, line_color="red",
            )

        # Axis
        self.fig.update_yaxes(range=[-50, 75], showticksuffix='all', ticksuffix="%")

    @classmethod
    def __set_color(cls, value) -> str:
        """
        Set color base on the values
        """
        if value <= 0:
            return "red"

        return "green"


class CategoriesOverviewArea(GraphTemplate):
    """
    Plot the expenses divided by main categories in an area stacked plot
    """

    def __init__(self, transactions):
        super().__init__(transactions)
        self.__create_plot()

    def __create_plot(self):
        """
        Create a subplot with all categories stacked in bars  sorted from more total
        expenses
        This graph does not distinguish between subcategories.
        """
        expenses = get_month_exp_by_category(self.transactions)

        for category, category_expenses in expenses.items():
            self.fig.add_trace(
                go.Scatter(
                    x=self.timeline,
                    y=list(category_expenses.values()),
                    stackgroup='one',
                    name=category,
                    mode='lines',
                )
            )


class IncomeExpenses(GraphTemplate):
    """
    Plot the expenses divided by main categories in an area stacked plot
    """

    def __init__(self, transactions):
        super().__init__(transactions)
        self.__create_plot()

    def __create_plot(self):
        """
        Create income/expenses subplot
        """
        expenses = get_monthly_total_expenses(self.transactions)
        income = get_monthly_total_income(self.transactions)

        # EXPENSES
        self.fig.add_trace(
            go.Scatter(
                x=self.timeline, y=list(expenses.values()),
                name="expenses", marker_color = "red"),
        )

        # Expenses trend
        expenses_trend = self._smooth_curve(list(expenses.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(
                x=self.timeline, y=expenses_trend,
                mode = "lines", name="Expenses smoothed",
            marker_color = "red", opacity=0.3),
        )

        # INCOME
        self.fig.add_trace(
            go.Scatter(
                x=self.timeline, y=list(income.values()), name="income", marker_color = "green"),
        )

        # Income trend
        income_trend = self._smooth_curve(list(income.values()), 0.9)
        self.fig.add_trace(
            go.Scatter(x=self.timeline, y=income_trend, mode = "lines", name="Income smoothed",
            marker_color = "green", opacity=0.3),
        )

        # Axis
        self.fig.update_yaxes(showticksuffix='all', ticksuffix="€")


class CategoriesOverviewBars(GraphTemplate):
    """
    Plot the expenses divided by main categories
    """

    def __init__(self, transactions: list[Transaction]):
        super().__init__(transactions)
        self.__create_plot()

    def __create_plot(self):
        """
        Create a subplot with all categories stacked in bars  sorted from more total
        expenses
        This graph does not distinguish between subcategories.
        """
        expenses = get_month_exp_by_category(self.transactions)

        for category, category_expenses in expenses.items():
            self.fig.add_trace(
                go.Bar(
                    name=category,
                    x=self.timeline,
                    y=list(category_expenses.values())
                )
          )

        self.fig.update_layout(barmode='stack')

        # Axis
        self.fig.update_yaxes(showticksuffix='all', ticksuffix="€")


class AverageExpensesYearBars(GraphTemplate):
    """
    Plot the average expenses by category per year
    """

    def __init__(self, transactions: list[Transaction]):
        super().__init__(transactions)
        self.timeline = get_expenses_years(transactions)
        self.__create_plot()

    def __create_plot(self):
        """
        Create a plot with all average expenses per category
        """
        expenses = get_category_average_expenses(self.transactions)

        for category, category_expenses in expenses.items():
            self.fig.add_trace(
                go.Bar(
                    name=category,
                    x=self.timeline,
                    y=list(category_expenses.values())
                )
          )

        self.fig.update_layout(barmode='stack')

        # Axis
        self.fig.update_yaxes(showticksuffix='all', ticksuffix="€")


class CategoryDetails(GraphTemplate):
    """
    Plot the expenses of a category in a bar graph as the sum of all subcategories
    """

    def __init__(self, transactions, category: str, subcategories: dict[str:dict[str:int|float]]):
        super().__init__(transactions=transactions)
        self.subcategories = subcategories
        self.category = category
        self.__create_plot()

    def __create_plot(self):
        """
        Create a subplot with all sub categories stacked in bars.
        """
        for subcategory, subcategory_expenses in self.subcategories.items():

            self.fig.add_trace(
                go.Bar(
                    name=subcategory,
                    x=self.timeline,
                    y=list(subcategory_expenses.values())
                )
            )


        self.fig.update_layout(barmode='stack')

        # Average
        category_expenses = get_month_exp_by_category(self.transactions)[self.category]

        category_avg = get_metric_average(category_expenses)
        self.fig.add_hline(
            y=category_avg, line_dash="dash",
            annotation_text=f'{self.category} average: ({category_avg:.2f}€)',
            annotation_position="bottom right"
        )


        # Axis
        self.fig.update_yaxes(showticksuffix='all', ticksuffix="€")


class CategoryYearAvg(GraphTemplate):
    """
    Plot the average of subcategories in a bar graph per month per year
    """

    def __init__(self, transactions, category: str, subcategories: dict[str:dict[str:int|float]]):
        super().__init__(transactions=transactions)
        self.subcategories = subcategories
        self.category = category
        self.timeline = get_expenses_years(transactions)
        self.__create_plot()

    def __create_plot(self):
        """
        Create a subplot with all sub categories stacked in bars.
        """
        for subcategory, subcategory_expenses in self.subcategories.items():
            self.fig.add_trace(
                go.Bar(
                    name=subcategory,
                    x=self.timeline,
                    y=list(subcategory_expenses['year'].values())
                )
            )


        self.fig.update_layout(barmode='stack')

        # Average
        # category_expenses = get_month_exp_by_category(self.transactions)[self.category]

        # category_avg = get_metric_average(category_expenses)
        # self.fig.add_hline(
        #     y=category_avg, line_dash="dash",
        #     annotation_text=f'{self.category} average: ({category_avg:.2f}€)',
        #     annotation_position="bottom right"
        # )


        # Axis
        self.fig.update_yaxes(showticksuffix='all', ticksuffix="€")


def get_overview_graphs(transactions: list[Transaction]) -> dict[str:str]:
    """
    Generate the graphs that summary all expenses
    """
    graph_list = {
        'Income and expenses': IncomeExpenses,
        'Balance': IncomeExpensesBalance,
        'Relative Balance': IncomeExpensesRelativeBalance,
        'Categories Overview Area': CategoriesOverviewArea,
        'Categories Overview Bars': CategoriesOverviewBars,
        'Categories Average expenses': AverageExpensesYearBars,
    }
    overview_graphs = []
    for name, graph in graph_list.items():
        overview_graphs.append(
            {
                'name': name,
                'graph': graph(transactions=transactions).get_html()
            }
        )
    return overview_graphs


def get_all_categories_detailed_bar_graphs(transactions: list[Transaction]):
    """
    Return a dict of graphs with all categories divided in subcategories. Structure:
    - Category
        \\_ Subcategory:
            \\_ Dates
    """
    expenses = get_month_exp_by_category_with_subcategories(transactions)
    graphs = []
    for category, cat_expenses in expenses.items():
        cat_details = CategoryDetails(transactions, category, cat_expenses)
        graphs.append(
            {
                'name': category,
                'graph': cat_details.get_html(),
            }
        )
    return graphs


def get_all_categories_avg_expense_per_year_bar_graphs(transactions: list[Transaction]):
    """
    Return a dict of graphs with all categories divided in subcategories. Structure:

    """
    expenses = get_avg_category_expense_per_month_in_year(transactions)

    graphs = []
    for category, cat_expenses in expenses.items():
        cat_details = CategoryYearAvg(transactions, category, cat_expenses['subcategories'])
        graphs.append(
            {
                'name': category,
                'graph': cat_details.get_html(),
            }
        )
    return graphs
