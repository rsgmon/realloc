from unittest import TestCase
from TradeManager.trade_manager import Model, TradeRequest
from TradeManager.test.test_data.test_data import model_request_both, model_request_instructions, raw_model, acc_inst_raw_model, acc_inst_no_model, acc_inst_two_models, model_request_raw_model, blank, no_port_raw_model, acc_inst_both_models, valid_request


class TestTradeRequest(TestCase):
    def setUp(self):
        pass
        self.trade_request = TradeRequest(valid_request)
        self.model = Model(self.trade_request.model_request)

    def test_set_model_request(self):
        self.assertRaises(Exception, TradeRequest, acc_inst_no_model)
        self.assertRaises(Exception, TradeRequest, acc_inst_two_models)
        self.assertEqual(self.trade_request.model_request, raw_model)

    def test_set_portfolio_request(self):
        self.assertRaises(Exception, TradeRequest, blank)
        self.assertRaises(Exception, TradeRequest, no_port_raw_model)
        self.assertEqual(len(self.trade_request.portfolio_request), 1)

    def test_set_model(self):
        self.assertEqual(len(self.model.model_positions),4)