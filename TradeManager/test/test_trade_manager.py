from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest
from TradeManager.allocation import TradeAccountMatrix, TradeSelector, TradeInstructions, TradeAllocator, SelectorSellMultipleAccounts
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.portfolio import Portfolio
from TradeManager.test.test_data.test_data import valid_request
import pandas as pd

class TestTradeManager(TestCase):
    def setUp(self):
        # self.trade_manager = TradeManager(valid_request)

        # self.trade_calculator = TradeCalculator(self.trade_manager.portfolio, self.trade_manager.model)

        self.trade_request = TradeRequest(valid_request)

    def test_trade_request(self):
        self.assertEqual(valid_request['portfolio_request'],self.trade_request.portfolio_request)
        self.assertEqual(valid_request['model_request']['raw_model'], self.trade_request.model_request)

#     def test_trade_calculator(self):
#         # print(self.trade_calculator.portfolio_trade_list)
#         # pd.to_pickle(self.trade_calculator.portfolio_trade_list, '.\/test_data\/trade_list.pkl')
#         self.assertEqual(self.trade_calculator.portfolio_trade_list['shares']['MMM'], -580)
#
# class TestAllocation(TestCase):
#     def setUp(self):
#         self.portfolio = pd.read_pickle('test_data/portfolio.pkl')
#         self.trade_list = pd.read_pickle('test_data/trade_list.pkl')
#         self.trades = pd.read_pickle('test_data/trades.pkl')
#         self.tam = TradeAccountMatrix(self.portfolio, self.trade_list)
#         self.trade_instructions = TradeInstructions()
#         self.allocator = TradeAllocator(self.portfolio, self.trade_list)
#
#     def test_tam_setup(self):
#         # print(self.trade_list)
#         # print(self.tam.trade_account_matrix)
#         pass
#
#     def test_trade_account_matrix(self):
#         self.tam.update_tam(self.trades)
#
#     def test_select_trade(self):
#         trade_selector = TradeSelector()
#         trade_selector.get_trades(self.tam.trade_account_matrix, self.portfolio.account_numbers)
#
#     def test_trade_instructions(self):
#         self.trade_instructions.trades=self.trades
#         self.trade_instructions.trades=self.trades
#         self.assertEqual(len(self.trade_instructions.trades), 4)
#
#     def test_selector_sell_multiple_accounts(self):
#         selector_sell_multiple_accounts = SelectorSellMultipleAccounts()
#         selector_sell_multiple_accounts._select_accounts(self.tam, self.portfolio.account_numbers)

    # def test_allocator_controller(self):
    #     self.allocator.allocate_trades()