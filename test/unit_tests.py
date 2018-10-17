from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest, Model, PriceRetriever, RawRequest
from TradeManager.allocation import TradeAccountMatrix, MultipleAccountTradeSelector, TradeInstructions, AllocationController, TradingLibrary, SingleAccountTradeSelector
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.portfolio import Portfolio, PostTradePortfolio
from test.test_data_generator import read_pickle
import pandas as pd
pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000

class TestRawRequest(TestCase):
    def test_raw_from_excel(self):
        request = RawRequest('xl', '.\/test_data\/sheets\/simple\/simple_101518.xlsx', test=True)
        print(request)

    def test_raw_request_validation(self):
        with self.assertRaises(RuntimeError) as cm:
            rr = RawRequest('test', {'data': {}})
            rr._empty_request()
        self.assertEqual(str(cm.exception), 'Your request was had no data.')
        with self.assertRaises(RuntimeError) as cm:
            rr = RawRequest('test', {'data':{"symbl": ["A"]}, 'index': ['model']})
            rr._missing_required_columns()
        self.assertEqual(str(cm.exception), "The following columns were missing: ['price', 'account_number', 'symbol', 'model_weight', 'shares', 'restrictions']")
        with self.assertRaises(RuntimeError) as cm:
            rr = RawRequest('test', {"data":{"symbol": ["ABC"], "price": 10, "account_number": "model", "shares": None, "restrictions": None, "model_weight": [0.5]}})
            rr._no_accounts()
        self.assertEqual(str(cm.exception), 'No accounts were found in your request.')

    def test_raw_request_model_row_validation(self):
        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["model"], "shares": [None], "restrictions": [None], "model_weight": [None]}})
            request._model_rows_validation()
        self.assertEqual('BlankWeight', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["model"], "shares": [None], "restrictions": [None], "model_weight": ['ght']}})
            request._model_rows_validation()
        self.assertEqual('NonNumericWeight', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["model"], "shares": [45], "restrictions": [None], "model_weight": [0.55]}})
            request._model_rows_validation()
        self.assertEqual('ShareQuantityOnModelLine', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["model"], "shares": ['45'], "restrictions": [None], "model_weight": [0.55]}})
            request._model_rows_validation()
        self.assertEqual('ShareQuantityOnModelLine', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["model"], "shares": ['0.45'], "restrictions": [None], "model_weight": [0.55]}})
            request._model_rows_validation()
        self.assertEqual('ShareQuantityOnModelLine', cm.exception.test_error_code)

    def test_raw_request_account_row_validation(self):
        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["gh-67"], "shares": [None], "restrictions": [None], "model_weight": [None]}})
            request._account_rows_validation()
        self.assertEqual('BlankShares', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["gh-67"], "shares": ["test"], "restrictions": [None], "model_weight": [None]}})
            request._account_rows_validation()
        self.assertEqual('NonNumericShares', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["gh-67"], "shares": [50], "restrictions": [None], "model_weight": [0.55]}})
            request._account_rows_validation()
        self.assertEqual('WeightOnAccountLine', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["gh-67"], "shares": [50], "restrictions": [None], "model_weight": ['0.55']}})
            request._account_rows_validation()
        self.assertEqual('WeightOnAccountLine', cm.exception.test_error_code)

        with self.assertRaises(RuntimeError) as cm:
            request = RawRequest('test', {"data":{"symbol": ["ABC"], "price": [10], "account_number": ["gh-67"], "shares": [50], "restrictions": [None], "model_weight": ['10']}})
            request._account_rows_validation()
        self.assertEqual('WeightOnAccountLine', cm.exception.test_error_code)

    def test_columns_stripped(self):
        request = RawRequest('test', {
            "data": {"symbol": ["ABC "], "price": [10], "account_number": ["gh-67"], "shares": [50],
                     "restrictions": [None], "model_weight": None}})
        request._validate_raw_request()
        self.assertEqual(len(request.raw_request['symbol'][0]),3)

    def test_has_price(self):
        request = RawRequest('xl', '.\/test_data\/sheets\/simple\/simple_101518.xlsx', test=True)
        # request = RawRequest('test', [{"symbol": "SPY", "price": float('NaN'), "account_number": "model", "shares": float('NaN'), "restrictions": float('NaN'), "model_weight": 0.5}, {"symbol": "MDY", "price": 349.07, "account_number": "model", "shares": float('NaN'), "restrictions": float('NaN'), "model_weight": 0.5}, {"symbol": "SPY", "price": 205, "account_number": "123-45", "shares": 30, "restrictions": float('NaN'), "model_weight": float('NaN')}, {"symbol": "account_cash", "price": 1, "account_number": "123-45", "shares": 1812.81, "restrictions": float('NaN'), "model_weight": float('NaN')}], test=True)
        request._has_price()
        request.raw_request.loc[[2],["price"]] = float('NaN')
        with self.assertRaises(RuntimeError) as cm:
            request._has_price()
        self.assertEqual(str(cm.exception), 'The following symbols are missing prices. {0}'.format(['SPY']))
        request.raw_request.loc[[1], ["price"]] = float('NaN')
        with self.assertRaises(RuntimeError) as cm:
            request._has_price()
        self.assertEqual(str(cm.exception), "The following symbols are missing prices. ['MDY' 'SPY']")

    def test_duplicate_prices(self):
        request = RawRequest('test', [{"symbol": "SPY", "price": float('NaN'), "account_number": "model", "shares": float('NaN'), "restrictions": float('NaN'), "model_weight": 0.5}, {"symbol": "MDY", "price": 349.07, "account_number": "model", "shares": float('NaN'), "restrictions": float('NaN'), "model_weight": 0.5}, {"symbol": "SPY", "price": 205, "account_number": "123-45", "shares": 30, "restrictions": float('NaN'), "model_weight": float('NaN')}, {"symbol": "account_cash", "price": 1, "account_number": "123-45", "shares": 1812.81, "restrictions": float('NaN'), "model_weight": float('NaN')}], test=True)
        request._duplicate_price()
        request.raw_request.loc[[0], ["price"]] = 100
        with self.assertRaises(RuntimeError) as cm:
            request._duplicate_price()
        self.assertEqual(str(cm.exception), 'The following symbols have two different prices. {0}'.format(['SPY']))
        request.raw_request.loc[[1], ["symbol"]] = 'SPY'
        with self.assertRaises(RuntimeError) as cm:
            request._duplicate_price()
        self.assertEqual(str(cm.exception), 'The following symbols have two different prices. {0}'.format(['SPY']))



class TestPortfolio(TestCase):

    def test_buys_Only(self):
        portfolio = Portfolio(
            read_pickle('.\/test_data\/trade_request_prices\/buy_only_multi_account_single_target_actual_request.pkl').portfolio_request,
            read_pickle('.\/test_data\/trade_request_prices\/buy_only_multi_account_single_target_actual_prices.pkl').prices)
        self.assertEqual(portfolio.portfolio_value, 2000.01)
        self.assertEqual(portfolio.portfolio_cash, 1000.01)
        self.assertEqual(len(portfolio.portfolio_positions), 1)

    def test_sells_Only(self):
        portfolio_request = read_pickle('test_data\/trade_request_prices\/single_account_model_multi_target_request.pkl')
        prices = read_pickle('test_data\/trade_request_prices\/single_account_model_multi_target_prices.pkl')
        portfolio = Portfolio(portfolio_request.portfolio_request, prices.prices)
        self.assertEqual(portfolio.portfolio_value, 21672.82)
        self.assertEqual(portfolio.portfolio_cash, 1258)
        self.assertEqual(portfolio.portfolio_positions['shares'].size, 3)
        self.assertEqual(portfolio.account_matrix.loc['FB', '45-33']['shares'], 98.2)
        self.assertEqual(portfolio.account_matrix['shares'].size, 3)

    def test_sells_buy(self):
        portfolio_request = read_pickle(
            'test_data\/trade_request_prices\/single_account_model_multi_target_request.pkl')
        prices = read_pickle('test_data\/trade_request_prices\/single_account_model_multi_target_prices.pkl')


class TestModel(TestCase):
    def test_empty_model(self):
        request = RawRequest('test', {
            "data": {"symbol": ["BHI", "FB", "ABC"], "account_number": ["45-33", "45-33", "45-33"],
                     "model_weight": [float('NaN'), float('NaN'), float('NaN')], "shares": [float('NaN'), 92, 74.5],
                     "price": [float('NaN'), float('NaN'), float('NaN')],
                     "restrictions": [float('NaN'), float('NaN'), float('NaN')]}})
        request._validate_raw_request()
        tradeRequest = TradeRequest(request)
        model = Model(tradeRequest.model_request, 'test')
        model._set_model_positions()
        self.assertEqual(len(model.model_positions), 0)

    def test_model_with_position_no_account_cash(self):
        request = RawRequest('test', {
            "data": {"symbol": ["BHI", "FB", "ABC"], "account_number": ["model", "45-33", "45-33"],
                     "model_weight": [0.10, float('NaN'), float('NaN')], "shares": [float('NaN'), 92, 74.5],
                     "price": [float('NaN'), float('NaN'), float('NaN')],
                     "restrictions": [float('NaN'), float('NaN'), float('NaN')]}})
        request._validate_raw_request()
        trade_request = TradeRequest(request)
        model = Model(trade_request.model_request, 'test')
        model._set_model_positions()
        self.assertEqual(len(model.model_positions), 1)

    def test_model_no_position_with_account_cash(self):
        request = RawRequest('test', {
            "data": {"symbol": ["account_cash", "FB", "ABC"], "account_number": ["model", "45-33", "45-33"],
                     "model_weight": [0.10, float('NaN'), float('NaN')], "shares": [float('NaN'), 92, 74.5],
                     "price": [float('NaN'), float('NaN'), float('NaN')],
                     "restrictions": [float('NaN'), float('NaN'), float('NaN')]}})
        request._validate_raw_request()
        trade_request = TradeRequest(request)
        model = Model(trade_request.model_request, 'test')
        model._set_model_positions()
        self.assertEqual(len(model.model_positions), 0)

    def test_model_with_position_with_account_cash(self):
        request = RawRequest('test', {
            "data": {"symbol": ["account_cash", "FB", "ABC"], "account_number": ["model", "model", "45-33"], "model_weight": [0.10, 0.15, float('NaN')], "shares": [float('NaN'), float('NaN'), 74.5], "price": [float('NaN'), float('NaN'), float('NaN')], "restrictions": [float('NaN'), float('NaN'), float('NaN')]}})
        request._validate_raw_request()
        trade_request = TradeRequest(request)
        model = Model(trade_request.model_request, 'test')
        model._set_model_positions()
        self.assertEqual(len(model.model_positions), 1)


class TestCalculator(TestCase):
    def test_buy_only(self):
        trade_calculator = TradeCalculator(read_pickle('.\/test_data\/portfolio_model_prices\/multi_account_single_target_actual_portfolio.pkl'), read_pickle('.\/test_data\/portfolio_model_prices\/multi_account_single_target_actual_model.pkl'), read_pickle('.\/test_data\/portfolio_model_prices\/multi_account_single_target_actual_prices.pkl').prices)
        self.assertEqual(trade_calculator.portfolio_trade_list.loc['GGG'].share_trades, 10)

    def test_sell_only_single_target(self):
        trade_calculator = TradeCalculator(read_pickle('.\/test_data\/portfolio_model_prices\/sell_only_multi_account_actual_single_target_portfolio.pkl'), read_pickle('.\/test_data\/portfolio_model_prices\/sell_only_multi_account_actual_single_target_model.pkl'), read_pickle('.\/test_data\/portfolio_model_prices\/sell_only_multi_account_actual_single_target_prices.pkl').prices)
        self.assertEqual(trade_calculator.portfolio_trade_list.loc['GGG'].share_trades, -122.5)

    def test_no_trades(self):
        base = '.\/test_data\/portfolio_model_prices\/'
        trade_calculator = TradeCalculator(read_pickle(base+'no_trades_portfolio.pkl'), read_pickle(base +'no_trades_model.pkl'), read_pickle(base+'no_trades_prices.pkl'))

    def test_sell_only(self):
        trade_calculator = TradeCalculator(read_pickle(           '.\/test_data\/portfolio_model_prices/sell_only_multi_account_target_actual_equal_portfolio.pkl'), read_pickle(         '.\/test_data\/portfolio_model_prices\/sell_only_multi_account_target_actual_equal_model.pkl'), read_pickle(            '.\/test_data\/portfolio_model_prices\/sell_only_multi_account_target_actual_equal_prices.pkl').prices)
        self.assertEqual(len(trade_calculator.portfolio_trade_list), 2)


class TAM(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()

    def test_tam_create_no_trades(self):
        portfolio = read_pickle('.\/test_data\/portfolios_port_trade_lists\/edge_cases\/no_trades_portfolio.pkl')
        port_trade_list = read_pickle('.\/test_data\/portfolios_port_trade_lists\/edge_cases\/no_trades_trade_calculator.pkl').portfolio_trade_list
        tam = TradeAccountMatrix(portfolio, port_trade_list)

    def test_tam_create_buy_only(self):
        tam = TradeAccountMatrix(read_pickle('.\/test_data\/portfolios_port_trade_lists\/buy_only\/multi_account_single_target_actual_portfolio.pkl'), read_pickle('.\/test_data\/portfolios_port_trade_lists\/buy_only\/multi_account_single_target_actual_trade_calculator.pkl').portfolio_trade_list)
        self.assertEqual(len(tam.trade_account_matrix), 1)
        self.assertEqual(tam.trade_account_matrix['share_trades'].sum(), 10)

    def test_tam_create_sell_only(self):
        tam = TradeAccountMatrix(read_pickle('.\/test_data\/portfolios_port_trade_lists\/sell_only\/multi_account_actual_equal_no_model_portfolio.pkl'), read_pickle('.\/test_data\/portfolios_port_trade_lists\/sell_only\/multi_account_actual_equal_no_model_trade_calculator.pkl').portfolio_trade_list)
        self.assertEqual(len(tam.trade_account_matrix), 2)
        self.assertEqual(tam.trade_account_matrix['share_trades'].sum(), -298.0)

    def test_update_share_trades(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_tam.pkl')
        tam.trade_account_matrix['size'] = pd.Series([0,-100,0,100,0,0,0,0], index=tam.trade_account_matrix.index)
        tam._update_share_trades()
        self.assertEqual(tam.trade_account_matrix.loc['GGG', '45-33']['share_trades'], 96)
        self.assertEqual(tam.trade_account_matrix.loc['HHH', '45-33']['share_trades'], 400)
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_tam.pkl')
        tam.trade_account_matrix['size'] = pd.Series([10], index=tam.trade_account_matrix.index)
        tam._update_share_trades()
        self.assertEqual(tam.trade_account_matrix.loc['GGG', '111-111']['share_trades'], 0)

    def test_update_cash(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_tam.pkl')
        tam.trade_account_matrix['size'] = pd.Series([10], index=tam.trade_account_matrix.index)
        tam._update_cash()
        self.assertEqual(tam.cash.shares.sum(),900.01)
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_tam.pkl')
        tam.trade_account_matrix['size'] = pd.Series([0, -100, 0, 100, 0, 0, 0, 0],index=tam.trade_account_matrix.index)
        tam._update_cash()
        self.assertEqual(tam.cash.shares.sum(), 36500)


class SellComplete(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.sell_complete

    def test_buy_only_multi_account_single_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertTrue(self.trade_instructions.trades.empty)

    def test_sell_only_multi_account_actual_equal_no_model(self):
        tam = read_pickle('.\/test_data\/tams\/sell_only\/multi_account_actual_equal_no_model_tam.pkl')
        if self.test_method(tam.trade_account_matrix):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, tuple([2,5]))

    def test_sell_only_multi_account_actual_no_model(self):
        tam = read_pickle('.\/test_data\/tams\/sell_only\/multi_account_actual_no_model_tam.pkl')
        if self.test_method(tam.trade_account_matrix):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, tuple([4,5]))

    def test_sell_only_multi_account_actual_single_target(self):
        tam = read_pickle('.\/test_data\/tams\/sell_only\/multi_account_actual_single_target_tam.pkl')
        if self.test_method(tam.trade_account_matrix):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, tuple([5,5]))

    # def test_sell_only_multi_account_target_actual_equal(self):
    #     tam = read_pickle('.\/test_data\/tams\/sell_only\/multi_account_target_actual_equal_tam.pkl')
    #     if self.test_method(tam.trade_account_matrix):
    #         self.trade_instructions.trades = tam.trade_account_matrix
    #     self.assertEqual(self.trade_instructions.trades.shape, tuple([0,0]))


class SellSmallestMultiple(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.sell_smallest_multiple

    def test_0(self):
        tam_object = read_pickle('.\/test_data\/tams\/sell_only\/sell_smallest_multiple_0_tam.pkl')
        tam = tam_object.trade_account_matrix
        if self.test_method(tam):
            self.trade_instructions.trades = tam
            self.assertEqual(tam.loc['DEF', '45-33']['size'], -400)
        else:
            self.fail()

    def test_1(self):
        tam_object = read_pickle('.\/test_data\/tams\/sell_only\/sell_smallest_multiple_1_tam.pkl')
        tam = tam_object.trade_account_matrix
        if self.test_method(tam):
            self.trade_instructions.trades = tam
            self.assertEqual(tam.loc['DEF', '45-33']['size'], -400)
            self.assertEqual(tam.loc['ABC', '111-111']['size'], -750)
        else:
            self.fail()

    def test_2(self):
        tam_object = read_pickle('.\/test_data\/tams\/sell_only\/sell_smallest_multiple_2_tam.pkl')
        tam = tam_object.trade_account_matrix
        if self.test_method(tam):
            self.trade_instructions.trades = tam
            self.assertEqual(tam.loc[tam['size'] < 0].shape, (2,5))
            self.assertEqual(tam.loc['DEF', '45-33']['size'], -300)
        else:
            self.fail()

    def test_3(self):
        """
        Tests that rows with complete sells are ignored.
        :return:
        """
        tam_object = read_pickle('.\/test_data\/tams\/sell_only\/sell_smallest_multiple_3_tam.pkl')
        tam = tam_object.trade_account_matrix
        if self.test_method(tam):
            self.trade_instructions.trades = tam
            self.assertEqual(tam.loc[tam['size'] < 0].shape, (2,5))
            self.assertEqual(tam.loc['DEF', '45-33']['size'], -400)
        else:
            self.fail()

    def test_4(self):
        tam_object = read_pickle('.\/test_data\/tams\/sell_only\/sell_smallest_multiple_4_tam.pkl')
        tam = tam_object.trade_account_matrix
        while self.test_method(tam):
            self.trade_instructions.trades = tam
            tam_object.update_tam()
        else:
            self.assertEqual(self.trade_instructions.trades.shape, (3,5))
            self.assertEqual(self.trade_instructions.trades.loc['DEF', '45-33']['size'], -400)


class BuySingleHolding(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_single_holding

    def test_buy_only_multi_account_single_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.fail()
        self.assertTrue(self.trade_instructions.trades.empty)

    def test_buy_only_multi_account_single_target_actual_02(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_02_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            self.assertEqual(self.trade_instructions.trades.shape, (1,5))

    def test_buy_only_multi_account_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.fail()
        self.assertTrue(self.trade_instructions.trades.empty)

    def test_buy_only_multi_account_target_single_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_single_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.fail()


class BuyMultipleEntire(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_multiple_entire

    def test_buy_only_multi_account_single_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/cover_all_buy_methods_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix

    def test_buy_only_multi_account_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (1, 5))
        tam.update_tam()
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (2, 5))


"""Currently not in use and tests will fail. Using BuyMultipleEntire
class BuyMultipleComplete(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_multiple_complete

    def test_buy_only_multi_account_single_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertTrue(self.trade_instructions.trades.empty)

    def test_buy_only_multi_account_single_target_actual_02(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_02_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertTrue(self.trade_instructions.trades.empty)

    def test_buy_only_multi_account_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (8, 5))
        tam.update_tam()
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (5, 5))

    def test_buy_only_multi_account_target_actual_02(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_02_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (9,5))

    def test_buy_only_multi_account_target_single_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_single_actual_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertTrue(self.trade_instructions.trades.empty)"""


"""Currently not in use and tests fail. Using BuyMultiplePartialOneTrade
class BuyMultiplePartial(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_multiple_partial

    # def test_buy_only_multi_account_single_target_actual(self):
    #     tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_tam.pkl')
    #     if self.test_method(tam.trade_account_matrix, tam.cash):
    #         self.trade_instructions.trades = tam.trade_account_matrix
    #     self.assertTrue(self.trade_instructions.trades.empty)

    def test_buy_only_multi_account_single_target_actual_02(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_actual_02_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (1, 5))

    # def test_buy_only_multi_account_target_actual(self):
    #     tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_tam.pkl')
    #     if self.test_method(tam.trade_account_matrix, tam.cash):
    #         self.trade_instructions.trades = tam.trade_account_matrix
    #     self.assertEqual(self.trade_instructions.trades.shape, (8, 5))
    #
    # def test_buy_only_multi_account_target_actual_02(self):
    #     tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_actual_02_tam.pkl')
    #     if self.test_method(tam.trade_account_matrix, tam.cash):
    #         self.trade_instructions.trades = tam.trade_account_matrix
    #     self.assertEqual(self.trade_instructions.trades.shape, (9,5))
    #
    # def test_buy_only_multi_account_target_single_actual(self):
    #     tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_single_actual_tam.pkl')
    #     if self.test_method(tam.trade_account_matrix, tam.cash):
    #         self.trade_instructions.trades = tam.trade_account_matrix
    #     self.assertTrue(self.trade_instructions.trades.empty)"""


class BuyMultiplePartialOneTrade(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_multiple_partial_one_trade

    def test_buy_only_multi_account_target_actual(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/buy_multiple_partial_one_trade_01_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (1, 5))

    def test_two_in_a_row(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/buy_multiple_partial_one_trade_01_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
        self.assertEqual(self.trade_instructions.trades.shape, (1, 5))
        tam.update_tam()
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            self.assertEqual(self.trade_instructions.trades.shape, (2, 5))


class BuySinglePartial(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_single_partial

    def test_01(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/buy_single_partial_01_tam.pkl')

        rows = 1
        while self.test_method(tam.trade_account_matrix, tam.cash):
            # print(tam.trade_account_matrix)
            self.trade_instructions.trades = tam.trade_account_matrix
            self.assertEqual(self.trade_instructions.trades.shape, (rows, 5))
            tam.update_tam()
            rows+=1

        # print('ins', self.trade_instructions.trades)

    # def test_02(self):
    #     tam = read_pickle('.\/test_data\/tams\/buy_only\/buy_single_partial_02_tam.pkl')
    #     rows = 1
    #     while self.test_method(tam.trade_account_matrix, tam.cash):
    #         self.trade_instructions.trades = tam.trade_account_matrix
    #         tam.update_tam()
    #         self.assertEqual(self.trade_instructions.trades.shape, (rows, 5))
    #         rows+=1
    #     else:
    #         self.assertEqual(self.trade_instructions.trades.iloc[0]['size'], 40)


class BuyNewComplete(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_new_complete

    def test_buy_only_multi_account_target_new_holding_only(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/buy_new_complete_01_tam.pkl')
        while self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            tam.update_tam()
        else:
            self.assertEqual(self.trade_instructions.trades.shape, (2, 5))

    def test_buy_only_multi_account_target_new_holding_sufficient_cash(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_new_holding_only_sufficient_cash_in_one_account_for_all_new_trades_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            self.assertEqual(tam.trade_account_matrix.loc['HHH', '111-111']['size'], 198)
        else:
            self.fail()

    def test_buy_only_all_3(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/cover_all_buy_methods_3_tam.pkl')
        rows = 1
        while self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            tam.update_tam()
            self.assertEqual(self.trade_instructions.trades.shape, (rows, 5))
            rows+=1
        else:
            self.assertEqual(self.trade_instructions.trades.iloc[0]['size'], 488)

    def test_buy_new_complete_2(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/buy_new_complete_2_tam.pkl')
        rows = 1
        while self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            tam.update_tam()
            self.assertEqual(self.trade_instructions.trades.shape, (rows, 5))
            rows+=1
        else:
            self.assertEqual(self.trade_instructions.trades.iloc[0]['size'], 488)


class BuyNewPartial(TestCase):
    def setUp(self):
        self.trading_library = TradingLibrary()
        self.trade_instructions = TradeInstructions()
        self.test_method = self.trading_library.buy_new_partial

    def test_buy_only_multi_account_target_new_holding_only_insufficient_cash(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_target_new_holding_only_insufficient_cash_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            self.assertEqual(tam.trade_account_matrix.loc['HHH', 'th6-453']['size'], 101)
        else:
            self.fail()

    def test_multi_account_single_target_new_only_insufficient_cash_tam(self):
        tam = read_pickle('.\/test_data\/tams\/buy_only\/multi_account_single_target_new_only_insufficient_cash_tam.pkl')
        if self.test_method(tam.trade_account_matrix, tam.cash):
            self.trade_instructions.trades = tam.trade_account_matrix
            self.assertEqual(tam.trade_account_matrix.loc['GGG', '111-111']['size'], 120)
        else:
            self.fail()


    """Note that I did not include cases for sell_only or buy_sell. In fact I deleted them. See log and explantion given on 11/27/17."""


class SellAllMethods(TestCase):
    def test_MultipleAccountTradeSelector(self):
        trade_selector = MultipleAccountTradeSelector(read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/sell_only\/cover_all_sell_methods_portfolio.pkl'), read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/sell_only\/cover_all_sell_methods_trade_calculator.pkl').portfolio_trade_list)
        trade_selector._get_sell_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.loc[('GHI', '45-33')]['size'], -100)
        self.assertEqual(trades.loc[('ABC', '56-66')]['size'], -690)

    def test_MultipleAccountTradeSelector_expanded(self):
        trade_selector = MultipleAccountTradeSelector(read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/sell_only\/cover_all_sell_methods_expanded_portfolio.pkl'), read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/sell_only\/cover_all_sell_methods_expanded_trade_calculator.pkl').portfolio_trade_list)
        trade_selector._get_sell_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.loc[('GHI', '45-33')]['size'], -100)
        self.assertEqual(trades.loc[('DEF', '111-111')]['size'], -412)
        self.assertEqual(trades.loc[('DEF', '56-66')]['size'], -200)

    def test_MultipleAccountTradeSelector_2(self):
        trade_selector = MultipleAccountTradeSelector(read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/sell_only\/cover_all_sell_methods_2_portfolio.pkl'), read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/sell_only\/cover_all_sell_methods_2_trade_calculator.pkl').portfolio_trade_list)
        trade_selector._get_sell_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.loc[('AAPL', '899-R')]['size'], -286)
        self.assertEqual(trades.loc[('NKE', 'ER-56')]['size'], -600)


class BuyAllMethods(TestCase):
    def test_MultipleAccountTradeSelector(self):
        trade_selector = MultipleAccountTradeSelector(read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_portfolio.pkl'), read_pickle('.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_trade_calculator.pkl').portfolio_trade_list)
        trade_selector._get_buy_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.shape, (6, 5))
        self.assertEqual(trades.loc[('GGG', '111-111')]['size'], 1086)

    def test_MultipleAccountTradeSelector_02(self):
        trade_selector = MultipleAccountTradeSelector(read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_2_portfolio.pkl'), read_pickle('.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_2_trade_calculator.pkl').portfolio_trade_list)
        trade_selector._get_buy_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.shape, (7, 5))

    def test_MultipleAccountTradeSelector_03(self):
        trade_selector = MultipleAccountTradeSelector(read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_3_portfolio.pkl'), read_pickle('.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_3_trade_calculator.pkl').portfolio_trade_list)
        trade_selector._get_buy_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.shape, (13, 5))

    def test_MultipleAccountTradeSelector_04(self):
        trade_selector = MultipleAccountTradeSelector(read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_3_portfolio.pkl'), read_pickle('.\/test_data\/portfolios_port_trade_lists\/buy_only\/cover_all_buy_methods_3_trade_calculator.pkl').portfolio_trade_list)
        trade_selector._get_buy_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.shape, (13, 5))


class AllTradeMethods(TestCase):
    def test_MultipleAccountTradeSelector_01(self):
        portfolio = read_pickle('.\/test_data\/portfolios_port_trade_lists\/sell_buy\/all_methods_1_portfolio.pkl')
        portfolio_trade_list = read_pickle('.\/test_data\/portfolios_port_trade_lists\/sell_buy\/all_methods_1_trade_calculator.pkl').portfolio_trade_list
        trade_selector = MultipleAccountTradeSelector(portfolio, portfolio_trade_list)
        trade_selector.get_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.shape, (16, 5))

    def test_MultipleAccountTradeSelector_2(self):
        portfolio = read_pickle('.\/test_data\/portfolios_port_trade_lists\/sell_buy\/all_methods_2_portfolio.pkl')
        portfolio_trade_list = read_pickle(
            '.\/test_data\/portfolios_port_trade_lists\/sell_buy\/all_methods_2_trade_calculator.pkl').portfolio_trade_list
        trade_selector = MultipleAccountTradeSelector(portfolio, portfolio_trade_list)
        trade_selector.get_trades()
        trades = trade_selector.trade_instructions.trades
        self.assertEqual(trades.shape, (14, 5))

    def test_MultipleAccounts_101518(self):
        portfolio = read_pickle('.\/test_data\/trade_instructions\/all_methods_101518_trade_instructions.pkl')
        print(vars(portfolio))

class TestDev(TestCase):
    pass

""" Deprecated see development log 10/17/18
class TestPriceRetriever(TestCase):
    def setUp(self): pass
        # self.raw_request_sell_only = RawRequest('xl',
        #     'test_data\/sheets\/sell_only\/multi_account_target_actual_equal.xlsx')
        # self.raw_request = RawRequest('xl',
        #     'test_data\/Trade Request Example.xlsx')
        # self.request_symbol_no_price = RawRequest('test', {"data":{"account": ["bgg"], "symbol": ["YYY"], "weight": [None], "shares": [None],"price": 'hjg', "restrictions": [None]}} )

    def test_initiate_price_retriever(self):
        self.assertTrue(PriceRetriever(self.raw_request))

    def test_price_retriever_add_prices_with_local_sample_prices(self):
        pr = PriceRetriever(self.raw_request)
        pr(test=True)
        self.assertGreater(pr.prices.sum().price, 1)

    def test_sells_only(self):
        pr = PriceRetriever(self.raw_request_sell_only)
        pr(test=True)
        self.assertGreater(pr.prices.sum().price, 1)

    def test_simple_request(self):
        simple_request = RawRequest('test',
                                    {"data":{"account": ["gt056"], "symbol": ["YYY"], "weight": None, "shares": 45,
                                          "price": 'hjg', "restrictions": None}})
        pr = PriceRetriever(simple_request)
        self.assertRaises(ValueError, pr)

    def test_port_rebalance(self):
        mock_raw_request = RawRequest('xl','test_data\/sheets\/port rebal for fithm.xlsx')
        print(mock_raw_request.raw_request)
        pr = PriceRetriever(mock_raw_request)
        pr(test=False)
        print(pr.raw_request)
        # print(pr.prices)

    # 05/30/17 passes but calls yahoo so not running at this point
    # def test_price_retriever_add_prices_with_yahoo_prices(self):
    #     pr = PriceRetriever(self.raw_request)
    #     pr()
    #     self.assertGreater(pr.prices.sum().price, 1)

    # def test_flag_no_price(self):
    #     pr = PriceRetriever(RawRequest('xl',
    #                                    'test_data\/Trade Request Example_missing_price.xlsx'))
    #     self.assertRaises(RuntimeError, pr, test=True, file_name='test_data\/prices.json', test_array_index=1)
    #     # 05/30/17 I've turned this test off for now as it calls yahoo. but as of date it worked.
    #     # self.assertRaises(RuntimeError, pr)
"""
