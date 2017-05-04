from unittest import TestCase
from TradeManager.trade_manager import Model, TradeRequest
from TradeManager.test.test_data.test_data import raw_model, acc_inst_no_model, acc_inst_two_models, blank, no_port_raw_model, trade_requests


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