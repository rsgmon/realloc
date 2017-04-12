from unittest import TestCase
from TradeManager.portfolio import Portfolio
from TradeManager.trade_manager import TradeRequest
from TradeManager.test.test_data.test_data import account_instructions, valid_request


class TestPortfolio(TestCase):
    def setUp(self):
        self.trade_request = TradeRequest(valid_request)
        self.portfolio = Portfolio()

    def test_get_portfolio(self):
        self.assertEqual(len(self.portfolio.get_portfolio_positions(self.trade_request.portfolio_request)),6)

    def test_get_portfolio_value(self):
        self.assertEqual(self.portfolio.get_portfolio_value(self.trade_request.portfolio_request), 161200.0)

    def test_testit(self):
        self.assertTrue(1)