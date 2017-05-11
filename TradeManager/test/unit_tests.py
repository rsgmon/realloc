from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest, Model
from TradeManager.allocation import TradeAccountMatrix, TradeSelector, TradeInstructions, TradeAllocator, SelectorSellMultipleAccounts
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.portfolio import Portfolio
from TradeManager.test.test_data.test_data import raw_model, acc_inst_no_model, acc_inst_two_models, blank, no_port_raw_model, trade_requests, trade_requests_keys
from TradeManager.test.test_data.test_data_generator import read_pickle
import pickle

"""one_holding_one_position
one_holding_zero_model
one_holding_two_holding_zero_model
one_holding_equal_weighted, one_holding_two_holding_two_position"""


class TestCalculator(TestCase):
    def setUp(self):
        self.mocks = read_pickle('.\/test_data\/mocks.pkl')

    def test_trade_calculator(self):
        for mock in self.mocks:
            t_calc = self.mocks[mock]['trade_calculator']
            self.assertLess(t_calc.portfolio_trade_list['shares']['MMM'], 0)


class TestAllocation(TestCase):
    def setUp(self):
        self.mocks = read_pickle('.\/test_data\/mocks.pkl')
        self.tam = TradeAccountMatrix(self.mocks['one_holding_equal_weighted']['portfolio'], self.mocks['one_holding_equal_weighted']['trade_calculator'])
        self.tam_sell_only = TradeAccountMatrix(self.mocks['one_holding_zero_model']['portfolio'],
                                      self.mocks['one_holding_zero_model']['trade_calculator'])
        self.trade_selector = TradeSelector()
        self.trades = self.trade_selector.get_trades(self.tam, self.mocks['one_holding_one_position']['portfolio'].account_numbers)
        self.trade_instructions = TradeInstructions()
        self.allocator = TradeAllocator(self.mocks['one_holding_one_position']['portfolio'], self.mocks['one_holding_one_position']['trade_calculator'])

    def test_tam_setup(self):
        self.assertGreater(len(self.tam.trade_account_matrix), 0)

    def test_update_sells_only_trade_account_matrix(self):
        tam_original = self.tam_sell_only.trade_account_matrix.copy()
        self.tam_sell_only.update_tam(self.trades)
        self.assertGreater(tam_original.ix[0,0], self.tam_sell_only.trade_account_matrix.ix[0,0])
        """need tests that checks updated tams are correct"""

    def test_cash_updated(self):
        tam_original_cash = self.tam_sell_only.cash.copy()
        self.tam_sell_only.update_tam(self.trades)
        self.assertGreater(self.tam_sell_only.cash.ix[0,0], tam_original_cash.ix[0,0])

    def test_select_trade(self):
        trade_selector = TradeSelector()
        # print(trade_selector.get_trades(self.tam, self.mocks['one_holding_one_position']['portfolio'].account_numbers))

    def test_trade_instructions(self):
        self.trade_instructions.trades=self.trades
        self.trade_instructions.trades=self.trades
        self.assertGreater(len(self.trade_instructions.trades), 0)

    def test_selector_sell_multiple_accounts(self):
        tam = TradeAccountMatrix(self.mocks['one_holding_two_holding_two_position']['portfolio'], self.mocks['one_holding_two_holding_two_position']['trade_calculator'])
        selector_sell_multiple_accounts = SelectorSellMultipleAccounts()
        print(selector_sell_multiple_accounts._select_accounts(tam, self.mocks['one_holding_two_holding_two_position']['portfolio'].account_numbers))

    def test_allocator_controller(self):
        self.allocator.allocate_trades()


class TestTradeRequest(TestCase):
    def setUp(self):
        self.trade_request = TradeRequest(trade_requests['one_holding_zero_model'])
        self.model = Model(self.trade_request.model_request)

    def test_trade_request(self):
        pass#print(self.model.model_positions)

    def test_set_model_request(self):
        self.assertRaises(Exception, TradeRequest, acc_inst_no_model)
        self.assertRaises(Exception, TradeRequest, acc_inst_two_models)

    def test_set_portfolio_request(self):
        self.assertRaises(Exception, TradeRequest, blank)
        self.assertRaises(Exception, TradeRequest, no_port_raw_model)

    def test_set_model(self):
        self.assertGreater(len(self.model.model_positions),0)


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