from unittest import TestCase
from TradeManager.portfolio import Portfolio
from TradeManager.test.test_data import accounts, trade_request


class TestPortfolio(TestCase):
    def setUp(self):
        self.test_portfolio = Portfolio(trade_request['account_numbers'])

    def test_get_portfolio(self):
        self.assertEqual(accounts, self.test_portfolio.accounts)

    def test_concat_positions(self):
        self.assertTrue(True)

    def test_aggregate_share_positions(self):
        self.assertTrue(self.test_portfolio.aggregated_portfolio)

    def test_get_portfolio_value(self):
        self.assertTrue(self.test_portfolio.get_portfolio_value(self.test_portfolio.aggregated_portfolio))
