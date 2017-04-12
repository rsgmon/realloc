from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.test.test_data.test_data import valid_request

class TestTradeManager(TestCase):
    def setUp(self):
        self.trade_manager = TradeManager(valid_request)
        self.trade_calculator = TradeCalculator(self.trade_manager.portfolio, self.trade_manager.model)
        self.trade_request = TradeRequest(valid_request)

    def test_trade_request(self):
        self.assertEqual(valid_request['portfolio_request'],self.trade_request.portfolio_request)
        self.assertEqual(valid_request['model_request']['raw_model'], self.trade_request.model_request)

    def test_trade_calculator(self):
        print(self.trade_calculator.portfolio_trade_list)