import pandas as pd
import numpy as np
from TradeManager.portfolio import Portfolio
from TradeManager.trade_calculator import TradeCalculator
import sys
from yahoo_finance import Share

class TradeManager(object):
    def __init__(self, trade_request=None):
        self.trade_request = TradeRequest(trade_request)
        self.model = self.get_model()
        self.portfolio = self.get_portfolio()
        self.portfolio_trades = self.get_portfolio_trades()
        # self.trades_by_account = self.allocate_trades()

    def get_model(self):
        return Model(self.trade_request.model_request)

    def get_portfolio(self):
        return Portfolio(self.trade_request.portfolio_request)

    def get_portfolio_trades(self):
        return TradeCalculator(self.portfolio, self.model)

    def allocate_trades(self):
        pass #return TradeAllocator(self.portfolio, self.portfolio_trades)

class RawRequest(object):
    def __init__(self, file_type_label, file_path):
        self.file_type_label = file_type_label
        self.file_path = file_path
        self._route_trade_request_type()

    def _route_trade_request_type(self):
        """
        Determines what file type the trade request was received in and routes to the appropriate opener.
        """
        if 'xl' in self.file_type_label:
            self.raw_request = pd.read_excel(self.file_path, engine='xlrd')
            # self.raw_request['symbol'].astype("int")
        elif 'csv' in 'csv':
            self.raw_request = pd.read_csv(self.file_path)
        elif 'json' in 'json':
            self.raw_request = pd.read_json(self.file_path)
            # todo must transform into pandas
        elif 'txt' in 'txt':
            pass  # todo
        else:
            return Exception

class TradeRequest(object):
    def __init__(self, raw_request):
        """ Return a Trade Request.
        Args:
        :param file_type_label: (str) has the extension which identifies file type
        :param file_path: (str) path to file (in production becomes the file itself)
        :param test_prices_file_path: (str) for testing only 
        """
        self.raw_request = raw_request.raw_request
        self.error = []
        self._set_trade_request()

    def _set_portfolio_request(self):
        try:
            # todo we need to add _get_accounts_from_brokers and incorporate
            self.portfolio_request = self.raw_request.loc[self.raw_request['account'] != 'model', ['account','symbol', 'shares', 'restrictions']]

        except KeyError as error:
            raise RuntimeError('Trade request must contain a portfolio request object. Yours did not') from error

    def _set_model_request(self):
        try:
            self.model_request = self.raw_request.loc[self.raw_request['account'] == 'model', ['symbol', 'weight']].set_index(['symbol'])
        except KeyError as error:
            raise RuntimeError('Trade request must contain a model request object. Yours did not') from error

    def _validate_fields(self, validation_request, instruction, raw):
        if instruction not in validation_request and raw not in validation_request:
            raise Exception('No model provided. You must provide instructions or a raw model.')
        if instruction in validation_request and raw in validation_request:
            if validation_request[instruction] != None and validation_request[raw] != None:
                raise Exception ('You must enter either model instructions or a model but not both.')
        if instruction in validation_request:
            if validation_request[instruction]:
                return validation_request[instruction] # we need to implement the retrieve_model_from_database method

    def _set_trade_request(self):
        self._set_portfolio_request()
        self._set_model_request()

    # todo The below method needs to be updated.
    # def _get_accounts_from_brokers(self, account_instructions ):
    #     if not isinstance(account_instructions, list):
    #         account_instructions = [account_instructions]
    #     accounts_from_broker = []
    #     for instruction in account_instructions:
    #         with open(instruction, 'r') as account:
    #             account = json.loads(account.read())
    #         accounts_from_broker.append(account)
    #     return accounts_from_broker

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])



class Model(object):
    def __init__(self, model_request=None):
        if model_request:
            self.model_request = model_request
            self.model_positions = self.get_raw_model_positions(self.model_request)

    def get_raw_model_positions(self, model_request):
        if not model_request['raw_model']['model_positions']:
            model_request['raw_model']['model_positions'].append({'symbol': 'placeholder', 'model_weight': 0})
        model_positions =  pd.DataFrame(model_request['raw_model']['model_positions'])
        model_positions.set_index('symbol', inplace=True)
        if 'cash' in model_positions.index:
            model_positions.drop('cash', inplace=True)
        return model_positions

    def retrieve_model_from_database(self):
        pass


class PriceRetriever(object):
    def __init__(self, raw_request):
        """
        Returns PriceRetriever object. If everything worked, .price_list contains the symbols and prices. If not returns an error.
        :param trade_request: object contains all symbols 
        :param file_name: (testing only) string pointing to file holding prices
        """
        self.error = []
        self.raw_request = raw_request.raw_request

    def __call__(self, file_name=None, test_array_index=0):
        self._set_symbol_retrieval_list()
        if file_name:
            self._test_set_remote_prices(file_name, test_array_index)
        else:
            self._set_remote_prices()
        self._combine_local_remote_prices()
        self._flag_no_price()


    def _set_symbol_retrieval_list(self):
        """
        Creates the list of symbols to retrieve from third party price provider.
        :return: none
        """
        symbols_only = self.raw_request[self.raw_request.loc[:,'symbol'].notnull()].copy()
        symbols_only['symbol'] = symbols_only.loc[:,'symbol'].astype(str)
        symbols_only = symbols_only[~symbols_only.loc[:,'symbol'].str.contains('account_cash', case=False) & symbols_only.loc[:,'price'].isnull()]
        self.price_retrieval_list = symbols_only

    def _combine_local_remote_prices(self):
        """        
        :return: none 
        """
        local = self.raw_request.loc[:,['symbol', 'price']].dropna().set_index(['symbol'])
        self.price_list = pd.concat([self.price_list, local])

    def _set_remote_prices(self):
        prices = []

        for symbol in self.price_retrieval_list:
            try:
                yahoo = Share(symbol=symbol)
                price = yahoo.get_price()
                prices.append(price)
            except (AttributeError, TypeError) as e:
                self.error.append( {symbol, 'Invalid symbol. Check for spaces or other non-alphanumeric characters'})
        self.price_list = pd.DataFrame(prices, index=self.price_retrieval_list, columns=['price']).apply(pd.to_numeric)

    def _test_set_remote_prices(self, file_name, test_array_index):
        """
         
        :param file_name: string, path to file
        :param test_array_index: int, position of test data in the array test data objects
        :return: none
        """
        import json

        with open(file_name, 'r') as ob:
            test_object = json.load(ob)
            self.price_list = pd.DataFrame(test_object[test_array_index]).set_index(['symbol'])

    def _flag_no_price(self):
        no_price = self.price_list[self.price_list.loc[:,'price'].isnull()]
        if len(no_price):
            print(no_price)
            raise RuntimeError(no_price.to_string())

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])