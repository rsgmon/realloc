from unittest import TestCase
from TradeManager.tradeManager import TradeManager

class TestTradeCalculator(TestCase):
    def setUp(self):
        self.trade_manager = TradeManager(5555)

    def test_get_dollar_trades(self):
        self.assertTrue(self.trade_manager)