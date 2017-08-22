from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest, Model, PriceRetriever, RawRequest
from TradeManager.allocation import TradeAccountMatrix, TradeSelector, TradeInstructions, AllocationController, \
    AccountSelectionLibrary, TradeSizingLibrary, SingleAccountTradeSelector, DualAccountTradeSelector
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.portfolio import Portfolio, PostTradePortfolio
from TradeManager.test.test_data_generator import read_pickle
import pandas as pd
import numpy as np


class TestTradeRequest(TestCase):
    def test_trade_request_validation(self):
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

    def test_trade_request_model_row_validation(self):
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

    def test_trade_request_account_row_validation(self):
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


class TestPriceRetriever(TestCase):
    def setUp(self):
        self.raw_request_sell_only = RawRequest('xl',
            'test_data\/sellsOnly\/TradeRequest.xlsx')
        self.raw_request = RawRequest('xl',
            'test_data\/Trade Request Example.xlsx')
        self.buy_only_request = RawRequest('xl', 'test_data\/buysOnly\/BuyOnlyRequest.xlsx')
        self.request_symbol_no_price = RawRequest('test', {"data":{"account": ["bgg"], "symbol": ["YYY"], "weight": [None], "shares": [None],"price": 'hjg', "restrictions": [None]}} )

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

    def test_sells_only_multiple_account_common_symbol(self):
        raw_request = read_pickle('.\/test_data\/sellsOnly\/sellsOnlyMultiple\/completedual\/request.pkl')
        pr = PriceRetriever(raw_request)
        pr()





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


class TestPortfolio(TestCase):

    def test_buys_Only(self):
        trade_request = read_pickle('test_data\/buysOnly\/request.pkl')
        prices = read_pickle('test_data\/buysOnly\/prices.pkl')
        portfolio = Portfolio(trade_request.portfolio_request, prices.prices)
        self.assertEqual(portfolio.portfolio_value, 18187.21)
        self.assertEqual(portfolio.portfolio_cash, 15687.21)
        self.assertEqual(len(portfolio.portfolio_positions), 1)

    def test_sells_Only(self):
        portfolio_request = read_pickle('test_data\/sellsOnly\/request.pkl')
        prices = read_pickle('test_data\/sellsOnly\/prices.pkl')
        portfolio = Portfolio(portfolio_request.portfolio_request, prices.prices)
        self.assertEqual(portfolio.portfolio_value, 29991.22)
        self.assertEqual(portfolio.portfolio_cash, 5687.22)
        self.assertEqual(portfolio.portfolio_positions['shares'].size, 3)
        self.assertEqual(portfolio.account_matrix.loc['FB', '45-33']['shares'], 98.2)
        self.assertEqual(portfolio.account_matrix['shares'].size, 4)


    def test_create_position_matrix(self):
        portfolio_request = read_pickle('test_data\/sellsOnly\/sellsOnlyMultiple\/dualAccounts\/request.pkl')
        prices = read_pickle('test_data\/sellsOnly\/sellsOnlyMultiple\/dualAccounts\/prices.pkl')
        portfolio = Portfolio(portfolio_request.portfolio_request, prices.prices)
        self.assertEqual(portfolio.portfolio_value, 39966.22)
        self.assertEqual(portfolio.portfolio_cash, 5687.22)
        self.assertEqual(portfolio.portfolio_positions['shares'].size, 5)
        self.assertEqual(portfolio.account_matrix.loc['FB', '45-33']['shares'], 98.2)
        self.assertEqual(portfolio.account_matrix['shares'].size, 6)


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
            "data": {"symbol": ["account_cash", "FB", "ABC"], "account_number": ["model", "model", "45-33"],
                     "model_weight": [0.10, 0.15, float('NaN')], "shares": [float('NaN'), float('NaN'), 74.5],
                     "price": [float('NaN'), float('NaN'), float('NaN')],
                     "restrictions": [float('NaN'), float('NaN'), float('NaN')]}})
        request._validate_raw_request()
        trade_request = TradeRequest(request)
        model = Model(trade_request.model_request, 'test')
        model._set_model_positions()
        self.assertEqual(len(model.model_positions), 1)


class TestCalculator(TestCase):
    def test_buy_only(self):
        portfolio = read_pickle('.\/test_data\/buysOnly\/portfolio.pkl')
        trade_request = read_pickle('.\/test_data\/buysOnly\/request.pkl')
        prices = read_pickle('.\/test_data\/buysOnly\/prices.pkl')
        model = Model(trade_request.model_request)
        trade_calculator = TradeCalculator(portfolio, model, prices.prices)
        self.assertEqual(trade_calculator.portfolio_trade_list.loc['AGG'].shares, 71)

    def test_single_sell_only(self):
        portfolio = read_pickle('.\/test_data\/sellsOnly\/sellsOnlySingle\/portfolio.pkl')
        trade_request = read_pickle('.\/test_data\/sellsOnly\/sellsOnlySingle\/request.pkl')

        prices = read_pickle('.\/test_data\/sellsOnly\/sellsOnlySingle\/prices.pkl')
        model = Model(trade_request.model_request)
        trade_calculator = TradeCalculator(portfolio, model, prices.prices)
        self.assertEqual(len(trade_calculator.portfolio_trade_list), 3)

    def test_single_buy_and_sell(self):
        portfolio = read_pickle('.\/test_data\/sellsAndBuys\/singleAccount\/portfolio.pkl')
        trade_request = read_pickle('.\/test_data\/sellsAndBuys\/singleAccount\/request.pkl')
        prices = read_pickle('.\/test_data\/sellsAndBuys\/singleAccount\/prices.pkl')
        model = Model(trade_request.model_request)
        trade_calculator = TradeCalculator(portfolio, model, prices.prices)
        self.assertEqual(len(trade_calculator.portfolio_trade_list), 3)
        self.assertEqual(trade_calculator.portfolio_trade_list['shares'][0], -352.0)
        self.assertEqual(trade_calculator.portfolio_trade_list['shares'][1], -47.0)

    def test_sell_only(self):
        portfolio = read_pickle('.\/test_data\/sellsOnly\/portfolio.pkl')
        prices = read_pickle('.\/test_data\/sellsOnly\/prices.pkl')
        model = read_pickle('.\/test_data\/sellsOnly\/model.pkl')
        trade_calculator = TradeCalculator(portfolio, model, prices.prices)
        self.assertEqual(len(trade_calculator.portfolio_trade_list), 3)


class TestAllocation(TestCase):
    def setUp(self):
        self.account_selector = AccountSelectionLibrary()
        self.trade_sizer = TradeSizingLibrary()
        self.single_buy_only_trade_list = read_pickle('.\/test_data\/buysOnly\/singleAccount\/trade_list.pkl')
        self.single_buy_only_portfolio = read_pickle('.\/test_data\/buysOnly\/singleAccount\/portfolio.pkl')
        self.sell_only_single_trade_list = read_pickle('.\/test_data\/sellsOnly\/sellsOnlySingle\/trade_list.pkl')
        self.sell_only_single_portfolio = read_pickle('.\/test_data\/sellsOnly\/sellsOnlySingle\/portfolio.pkl')
        self.sell_only_multiple_trade_list = read_pickle('.\/test_data\/sellsOnly\/trade_list.pkl')
        self.sell_only_multiple_portfolio = read_pickle('.\/test_data\/sellsOnly\/portfolio.pkl')
        self.single_buy_sell_trade_list = read_pickle('.\/test_data\/sellsAndBuys\/singleAccount\/trade_list.pkl')
        self.single_buy_sell_portfolio = read_pickle(            '.\/test_data\/sellsAndBuys\/singleAccount\/portfolio.pkl')


    def test_tam_creation(self):
        tam = TradeAccountMatrix(self.single_buy_only_portfolio, self.single_buy_only_trade_list.portfolio_trade_list)
        self.assertEqual(len(tam.trade_account_matrix), 2)
        self.assertEqual(len(tam.trade_account_matrix.columns), 4)
        self.assertEqual(tam.trade_account_matrix['shares'].sum(), 41)

    def test_TradeSelector(self):
        trade_selector = TradeSelector(self.sell_only_single_portfolio, self.sell_only_single_trade_list.portfolio_trade_list)
        self.assertEqual(trade_selector._has_buys(), False)

    def test_single_buy_only(self):
        trade_selector = SingleAccountTradeSelector(self.single_buy_only_portfolio, self.single_buy_only_trade_list.portfolio_trade_list)
        trade_selector.get_trades()
        self.assertEqual(len(trade_selector.trade_instructions.trades), 2)

    def test_SingleAccountTradeSelector(self):
        trade_selector = SingleAccountTradeSelector(self.sell_only_single_portfolio, self.sell_only_single_trade_list.portfolio_trade_list)
        trade_selector.get_trades()
        self.assertEqual(len(trade_selector.trade_instructions.trades),3 )

    def test_selectDualSell(self):
        tam = TradeAccountMatrix(self.sell_only_multiple_portfolio, self.sell_only_multiple_trade_list.portfolio_trade_list)
        t = tam.working_trade_account_matrix
        t['trade_account'] = self.account_selector.sell_single_holding(tam.working_trade_account_matrix, tam.account_numbers)
        self.assertEqual(t[t.loc[:,'trade_account']=='45-33']['trade_account'].size, 2)
        sizer = self.trade_sizer.sell_single_holding(t)
        self.assertEqual(sizer['size'].dropna().size, 2)


    def test_update_tam_dual_complete_sell_only(self):
        raw_update = pd.DataFrame({'45-33': {'BHI': 352.0, 'FB': 98.200000000000003, 'GGG': 74.5}, 'size': {'BHI': -352.0, 'FB': -98.200000000000003, 'GGG': np.nan}, 'trade_account': {'BHI': '45-33', 'FB': '45-33', 'GGG': 0}, 'price': {'BHI': 55.0, 'FB': 20.0, 'GGG': 20.0}, 'dollar_trades': {'BHI': -19360.0, 'FB': -1964.0, 'GGG': -2980.0}, 'shares': {'BHI': -352.0, 'FB': -98.200000000000003, 'GGG': -149.0}, '111-111': {'BHI': 0.0, 'FB': 0.0, 'GGG': 74.5}})
        tam = TradeAccountMatrix(self.sell_only_multiple_portfolio,self.sell_only_multiple_trade_list.portfolio_trade_list)
        trades = tam._prepare_for_tam_update(raw_update)
        self.assertEqual(trades.loc[:,'shares'].size, 2)
        tam._update_trades(trades)
        self.assertEqual(tam.trade_account_matrix.loc['BHI','shares'], 0)
        self.assertEqual(tam.trade_account_matrix.loc['GGG', 'shares'], -149)
        tam._update_holdings(trades)
        self.assertEqual(tam.trade_account_matrix.loc['BHI', '45-33'], 0)
        tam._update_cash(trades)
        self.assertEqual(tam.cash.loc['45-33', 'cash'], 27011)


    def test_dual_sell_only_complete_one_symbol(self):
        tam = TradeAccountMatrix(read_pickle('.\/test_data\/sellsOnly\/sellsOnlyMultiple\/completedual\/portfolio.pkl'), read_pickle('.\/test_data\/sellsOnly\/sellsOnlyMultiple\/completedual\/trade_list.pkl').portfolio_trade_list)
        accounts = self.account_selector.sell_complete(tam.working_trade_account_matrix, tam.account_numbers)


    def test_new_tam_creation(self):
        portfolio = read_pickle('.\/test_data\/sellsOnly\/sellsOnlyMultiple\/completedual\/portfolio.pkl')
        portfolio._set_position_matrix()
        tam = TradeAccountMatrix(portfolio, read_pickle('.\/test_data\/sellsOnly\/sellsOnlyMultiple\/completedual\/trade_list.pkl').portfolio_trade_list)
        tam._construct_trade_account_matrix_2(portfolio.position_matrix, tam.portfolio_trade_list)



    def test_SingleBuySell(self):
        trade_selector = SingleAccountTradeSelector(self.single_buy_sell_portfolio, self.single_buy_sell_trade_list.portfolio_trade_list)
        trade_selector.get_trades()
        self.assertEqual(len(trade_selector.trade_instructions.trades), 3)
