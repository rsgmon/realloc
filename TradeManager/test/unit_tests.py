from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest, Model, PriceRetriever, RawRequest
from TradeManager.allocation import TradeAccountMatrix, TradeSelector, TradeInstructions, AllocationController, \
    SelectorSellMultipleAccounts,\
    SingleAccountTradeSelector
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.portfolio import Portfolio, PostTradePortfolio
from TradeManager.test.test_data_generator import read_pickle


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


        #
        # def test_portfolio_request(self):
        #     raw_request_sell_only = RawRequest('xl', 'test_data\/sellsOnly\/TradeRequest.xlsx')
        #     self.assertEqual(len(TradeRequest(raw_request_sell_only).portfolio_request) , 6)
        #     self.assertEqual(len(TradeRequest(self.raw_request_buy_only).model_request), 2)
        #
        # def test_model_request(self):
        #     self.assertEqual(TradeRequest(self.raw_request_sell_only).model_request, None)
        #     self.assertEqual(len(TradeRequest(self.raw_request_buy_only).model_request), 2)

    def test_model_request_setup_when_no_model_specified(self):
        request = RawRequest('test', {
            "data": {"symbol": ["BHI", "FB", "ABC"],"account_number": ["45-33", "45-33", "45-33"],  "model_weight": [float('NaN'), float('NaN'), float('NaN')],"shares": [352,92,74.5], "price": [55, float('NaN'), float('NaN')],
                     "restrictions": [float('NaN'), float('NaN'), float('NaN')]}})
        request._validate_raw_request()
        trade_request = TradeRequest(request)
        self.assertEqual(trade_request.model_request.loc['account_cash'][0], 1)


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




    # 05/30/17 passes but calls yahoo so not running at this point
    # def test_price_retriever_add_prices_with_yahoo_prices(self):
    #     pr = PriceRetriever(self.raw_request)
    #     pr()
    #     self.assertGreater(pr.prices.sum().price, 1)

    def test_flag_no_price(self):
        pr = PriceRetriever(RawRequest('xl',
                                       'test_data\/Trade Request Example_missing_price.xlsx'))
        self.assertRaises(RuntimeError, pr, test=True, file_name='test_data\/prices.json', test_array_index=1)
        # 05/30/17 I've turned this test off for now as it calls yahoo. but as of date it worked.
        # self.assertRaises(RuntimeError, pr)


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
        self.assertEqual(len(portfolio.portfolio_positions), 3)

    def test_post_trade_portfolio(self):
        portfolio_request = read_pickle('test_data\/buysOnly\/singleAccount\/request.pkl')
        prices = read_pickle('test_data\/buysOnly\/singleAccount\/prices.pkl')
        allocation = read_pickle('test_data\/buysOnly\/singleAccount\/allocation.pkl')
        pre = Portfolio(portfolio_request.portfolio_request,prices.prices)
        post = PostTradePortfolio(allocation, portfolio_request.portfolio_request,prices.prices)
        self.assertEqual(pre.portfolio_value, post.portfolio_value)



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
        self.single_buy_only_trade_list = read_pickle('.\/test_data\/buysOnly\/singleAccount\/trade_list.pkl')
        self.single_buy_only_portfolio = read_pickle('.\/test_data\/buysOnly\/singleAccount\/portfolio.pkl')
        self.sell_only_single_trade_list = read_pickle('.\/test_data\/sellsOnly\/sellsOnlySingle\/trade_list.pkl')
        self.sell_only_single_portfolio = read_pickle('.\/test_data\/sellsOnly\/sellsOnlySingle\/portfolio.pkl')
        self.sell_only_multiple_trade_list = read_pickle('.\/test_data\/sellsOnly\/trade_list.pkl')
        self.sell_only_multiple_portfolio = read_pickle('.\/test_data\/sellsOnly\/portfolio.pkl')
        self.single_buy_sell_trade_list = read_pickle('.\/test_data\/sellsAndBuys\/singleAccount\/trade_list.pkl')
        self.single_buy_sell_portfolio = read_pickle(            '.\/test_data\/sellsAndBuys\/singleAccount\/portfolio.pkl')

    def test_TradeSelector(self):
        trade_selector = TradeSelector(self.sell_only_single_portfolio, self.sell_only_single_trade_list.portfolio_trade_list)
        self.assertEqual(trade_selector._has_buys(), False)

    def test_single_buy_only(self):
        trade_selector = SingleAccountTradeSelector(self.single_buy_only_portfolio, self.single_buy_only_trade_list.portfolio_trade_list)
        trade_selector._select_accounts()
        self.assertEqual(len(trade_selector.trade_instructions.trades), 2)

    def test_SingleAccountTradeSelector(self):
        trade_selector = SingleAccountTradeSelector(self.sell_only_single_portfolio, self.sell_only_single_trade_list.portfolio_trade_list)
        trade_selector._select_accounts()
        self.assertEqual(len(trade_selector.trade_instructions.trades),3 )

    def test_MultipleSellOnly(self):
        trade_selector = TradeSelector(self.sell_only_multiple_portfolio, self.sell_only_multiple_trade_list.portfolio_trade_list)
        self.assertEqual(len(trade_selector.trade_instructions.trades), 0)

    def test_SingleBuySell(self):
        trade_selector = SingleAccountTradeSelector(self.single_buy_sell_portfolio, self.single_buy_sell_trade_list.portfolio_trade_list)
        trade_selector._select_accounts()
        self.assertEqual(len(trade_selector.trade_instructions.trades), 3)
