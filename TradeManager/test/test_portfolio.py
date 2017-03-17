from unittest import TestCase
from TradeManager.portfolio import Portfolio
from TradeManager.test.test_data.test_data import accounts, trade_request, account_instructions


class TestPortfolio(TestCase):
    def setUp(self):
        self.portfolio = Portfolio(account_instructions)

    def test_get_portfolio(self):
        portfolio_positions = self.portfolio._get_accounts_from_brokers(self.portfolio.account_instructions)
        self.assertEqual(len(portfolio_positions[0]), 2)

    def test_concat_positions(self):
        pandaized_position = self.portfolio._pandaize_positions()
        self.assertEqual(len(pandaized_position), 3)

    def test_aggregate_share_positions(self):
        aggregated_portfolio_positions = self.portfolio._aggregate_share_positions()
        print(aggregated_portfolio_positions)

    # def test_get_portfolio_value(self):
    #     self.assertTrue(self.portfolio.get_portfolio_value(self.portfolio.aggregated_portfolio))
