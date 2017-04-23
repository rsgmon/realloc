from unittest import TestCase
from TradeManager.portfolio import Portfolio
from TradeManager.trade_manager import TradeRequest
from TradeManager.test.test_data.test_data import account_instructions, valid_request

class TestPortfolio(TestCase):
    def setUp(self):
        self.trade_request = TradeRequest(valid_request)
        self.portfolio = Portfolio(self.trade_request.portfolio_request)

    def test_get_portfolio(self):
        self.assertEqual(len(self.portfolio.get_portfolio_positions(self.trade_request.portfolio_request)),8)

    def test_get_portfolio_value(self):
        self.assertEqual(self.portfolio.get_portfolio_value(self.trade_request.portfolio_request), 79500.0)

    def test_create_account_matrix(self):
        self.assertTrue(type(self.portfolio.account_matrix))

    def test_account_numbers(self):
        print(self.portfolio.account_numbers)