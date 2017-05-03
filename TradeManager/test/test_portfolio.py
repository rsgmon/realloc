from unittest import TestCase
from TradeManager.portfolio import Portfolio
from TradeManager.trade_manager import TradeRequest
from TradeManager.test.test_data.test_data import account_instructions, trade_requests, trade_requests_keys
import pandas as pd
import pprint

class TestPortfolio(TestCase):
    def setUp(self):
        self.trade_requests = [TradeRequest(trade_requests[value]) for value in trade_requests]
        self.portfolios = [Portfolio(value.portfolio_request) for value in self.trade_requests]
        self.trade_request_dict = dict(zip(trade_requests_keys, self.trade_requests))
        # pd.to_pickle(self.portfolio, '.\/test_data\/portfolio.pkl')

    def test_print_portfolio_details(self):
        print(self.portfolios[0])

    def test_portfolio_attributes(self):
        for portfolio in self.portfolios:
            self.assertGreater(len(portfolio.portfolio_positions),0)
            self.assertGreater(portfolio.portfolio_value, 0)

    def test_create_account_matrix(self):
        portfolio = Portfolio(self.trade_request_dict['one_holding_zero_model'].portfolio_request)
        self.assertGreater(len(portfolio.account_matrix), 0)

    def test_account_numbers(self):
        self.assertGreater(len(self.portfolios[0].account_numbers), 0)

    def test_get_cash_matrix(self):
        cash_matrix = self.portfolios[0].set_cash_matrix()
        self.assertGreater(cash_matrix.loc['22-22',:][0], 0)

    def test_get_price_matrix(self):
        self.assertGreaterEqual(len(self.portfolios[0].cash_matrix), 1)