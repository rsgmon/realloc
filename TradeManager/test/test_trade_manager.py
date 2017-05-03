from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest, Model
from TradeManager.allocation import TradeAccountMatrix, TradeSelector, TradeInstructions, TradeAllocator, SelectorSellMultipleAccounts
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.portfolio import Portfolio
from TradeManager.test.test_data.test_data import trade_requests, trade_requests_keys
from TradeManager.test.test_data.test_data_generator import read_pickle
import pickle

"""one_holding_one_position
one_holding_zero_model
one_holding_two_holding_zero_model
one_holding_equal_weighted"""



class TestTradeManager(TestCase):
    def setUp(self):
        self.trade_request = TradeRequest(trade_requests['one_holding_equal_weighted'])
        self.portfolio = Portfolio(self.trade_request.portfolio_request)
        self.model = Model(self.trade_request.model_request)
        self.trade_calculator = TradeCalculator(self.portfolio, self.model)

    def test_trade_calculator(self):
        # pd.to_pickle(self.trade_calculator.portfolio_trade_list, '.\/test_data\/trade_list.pkl')
        self.assertEqual(self.trade_calculator.portfolio_trade_list['shares']['MMM'], -375)

class TestAllocation(TestCase):
    def setUp(self):
        self.mocks = read_pickle('.\/test_data\/mocks.pkl')
        self.tam = TradeAccountMatrix(self.mocks['one_holding_one_position']['portfolio'], self.mocks['one_holding_one_position']['trade_calculator'])
        self.trade_selector = TradeSelector()
        self.trades = self.trade_selector.get_trades(self.tam, self.mocks['one_holding_one_position']['portfolio'].account_numbers)
        self.trade_instructions = TradeInstructions()
        self.allocator = TradeAllocator(self.mocks['one_holding_one_position']['portfolio'], self.mocks['one_holding_one_position']['trade_calculator'])

    def test_show_mocks(self):
        p = self.mocks['one_holding_one_position']['portfolio']
        print(p.portfolio_positions)
        print(p.account_matrix)
        print(p.cash_matrix)
        c = self.mocks['one_holding_one_position']['trade_calculator']
        print(c.portfolio_trade_list)
        print(self.trades)

    def test_tam_setup(self):
        self.assertGreater(len(self.tam.trade_account_matrix), 0)

    def test_trade_account_matrix(self):
        tam_original = self.tam.trade_account_matrix.copy()
        self.tam.update_tam(self.trades)
        print(self.tam.trade_account_matrix)
        """need tests that checks updated tams are correct"""

    def test_select_trade(self):
        trade_selector = TradeSelector()
        trade_selector.get_trades(self.tam, self.mocks['one_holding_one_position']['portfolio'].account_numbers)

    def test_trade_instructions(self):
        self.trade_instructions.trades=self.trades
        self.trade_instructions.trades=self.trades
        self.assertGreater(len(self.trade_instructions.trades), 0)

    def test_selector_sell_multiple_accounts(self):
        selector_sell_multiple_accounts = SelectorSellMultipleAccounts()
        selector_sell_multiple_accounts._select_accounts(self.tam, self.mocks['one_holding_one_position']['portfolio'].account_numbers)

    def test_allocator_controller(self):
        self.allocator.allocate_trades()