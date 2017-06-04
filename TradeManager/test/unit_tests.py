from unittest import TestCase
from TradeManager.trade_manager import TradeManager, TradeRequest, Model, PriceRetriever, RawRequest
from TradeManager.allocation import TradeAccountMatrix, TradeSelector, TradeInstructions, TradeAllocator, SelectorSellMultipleAccounts
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.portfolio import Portfolio
from TradeManager.test.test_data.test_data_generator import read_pickle


class TestAllocation(TestCase):
    def setUp(self):
        self.trade_list= read_pickle('.\/test_data\/trade_list.pkl')
        self.portfolio = read_pickle('.\/test_data\/portfolio.pkl')
        self.tam = TradeAccountMatrix(self.portfolio, self.trade_list)
        # self.tam_sell_only = TradeAccountMatrix(self.trade_list['one_holding_zero_model']['portfolio'],
        #                               self.trade_list['one_holding_zero_model']['trade_calculator'])
        # self.trade_selector = TradeSelector()
        # self.trades = self.trade_selector.get_trades(self.tam, self.trade_list['one_holding_one_position']['portfolio'].account_numbers)
        # self.trade_instructions = TradeInstructions()
        # self.allocator = TradeAllocator(self.trade_list['one_holding_one_position']['portfolio'], self.trade_list['one_holding_one_position']['trade_calculator'])

    def test_tam_setup(self):
        self.assertGreater(len(self.tam.trade_account_matrix), 0)
    #
    # def test_update_sells_only_trade_account_matrix(self):
    #     tam_original = self.tam_sell_only.trade_account_matrix.copy()
    #     self.tam_sell_only.update_tam(self.trades)
    #     self.assertGreater(tam_original.ix[0,0], self.tam_sell_only.trade_account_matrix.ix[0,0])
    #     """need tests that checks updated tams are correct"""
    #
    # def test_cash_updated(self):
    #     tam_original_cash = self.tam_sell_only.cash.copy()
    #     self.tam_sell_only.update_tam(self.trades)
    #     self.assertGreater(self.tam_sell_only.cash.ix[0,0], tam_original_cash.ix[0,0])
    #
    # def test_select_trade(self):
    #     trade_selector = TradeSelector()
    #     # print(trade_selector.get_trades(self.tam, self.trade_list['one_holding_one_position']['portfolio'].account_numbers))
    #
    # def test_trade_instructions(self):
    #     self.trade_instructions.trades=self.trades
    #     self.trade_instructions.trades=self.trades
    #     self.assertGreater(len(self.trade_instructions.trades), 0)
    #
    # def test_selector_sell_multiple_accounts(self):
    #     tam = TradeAccountMatrix(self.trade_list['one_holding_two_holding_two_position']['portfolio'], self.trade_list['one_holding_two_holding_two_position']['trade_calculator'])
    #     selector_sell_multiple_accounts = SelectorSellMultipleAccounts()
    #     print(selector_sell_multiple_accounts._select_accounts(tam, self.trade_list['one_holding_two_holding_two_position']['portfolio'].account_numbers))
    #
    # def test_allocator_controller(self):
    #     self.allocator.allocate_trades()


class TestCalculator(TestCase):
    def setUp(self):
        self.portfolio = read_pickle('.\/test_data\/portfolio.pkl')
        self.trade_request = read_pickle('.\/test_data\/request.pkl')
        self.prices = read_pickle('.\/test_data\/prices.pkl')
        self.model = self.trade_request.model_request

    def test_trade_calculator(self):
        trade_calculator = TradeCalculator(self.portfolio, self.model, self.prices)


class TestTradeRequest(TestCase):
    def setUp(self):
        self.raw_request = RawRequest(read_pickle('test_data\/excel_request.pkl'), 'test_data\/Trade Request Example.xlsx')

    def test_trade_request_attributes(self):
        trade_request = TradeRequest(self.raw_request)
        self.assertGreater(len(trade_request.portfolio_request), 0)
        self.assertGreater(len(trade_request.model_request), 0)


class TestPriceRetriever(TestCase):
    def setUp(self):
        self.raw_request = RawRequest(read_pickle('test_data\/excel_request.pkl'),'test_data\/Trade Request Example.xlsx')

    def test_initiate_price_retreiver(self):
        self.assertTrue(PriceRetriever(self.raw_request))

    def test_price_retriever_add_prices_with_local_sample_prices(self):
        pr = PriceRetriever(self.raw_request)
        pr(file_name='test_data\/prices.json', test_array_index=0)
        self.assertGreater(pr.prices.sum().price, 1)

    # 05/30/17 passes but calls yahoo so not running at this point
    # def test_price_retriever_add_prices_with_yahoo_prices(self):
    #     pr = PriceRetriever(self.raw_request)
    #     pr()
    #     self.assertGreater(pr.prices.sum().price, 1)

    def test_flag_no_price(self):
        pr = PriceRetriever(RawRequest(read_pickle('test_data\/excel_request.pkl'),'test_data\/Trade Request Example_missing_price.xlsx'))
        self.assertRaises(RuntimeError, pr, file_name='test_data\/prices.json', test_array_index=1)
        # 05/30/17 I've turned this test off for now as it calls yahoo. but as of date it worked.
        # self.assertRaises(RuntimeError, pr)


class TestPortfolio(TestCase):
    def setUp(self):
        self.portfolio_request = read_pickle('test_data\/request.pkl')
        self.prices = read_pickle('test_data\/prices.pkl')
        self.portfolio = Portfolio(self.portfolio_request.portfolio_request, self.prices.prices)

    def test_print_portfolio_details(self):
        print(self.portfolio)


    # def test_portfolio_attributes(self):
    #     for portfolio in self.portfolios:
    #         self.assertGreater(len(portfolio.portfolio_positions),0)
    #         self.assertGreater(portfolio.portfolio_value, 0)
    #
    # def test_create_account_matrix(self):
    #     portfolio = Portfolio(self.trade_request_dict['one_holding_zero_model'].portfolio_request)
    #     self.assertGreater(len(portfolio.account_matrix), 0)
    #
    # def test_account_numbers(self):
    #     self.assertGreater(len(self.portfolios[0].account_numbers), 0)
    #
    # def test_get_cash_matrix(self):
    #     cash_matrix = self.portfolios[0].set_cash_matrix()
    #     self.assertGreater(cash_matrix.loc['22-22',:][0], 0)
    #
    # def test_get_price_matrix(self):
    #     self.assertGreaterEqual(len(self.portfolios[0].cash_matrix), 1)