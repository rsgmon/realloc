import pandas as pd
import os
from TradeManager.portfolio import Portfolio, PostTradePortfolio
from TradeManager.trade_calculator import TradeCalculator
from TradeManager.allocation import AllocationController
import math
from yahoo_finance import Share
from numbers import Number
from pandas.api.types import is_numeric_dtype


class TradeManager(object):
    def __init__(self, file_type=None, path=None):
        self.raw_request = RawRequest(file_type, path)
        self.trade_request = TradeRequest(self.raw_request)
        self.prices = self.get_prices()
        self.model = Model(self.trade_request.model_request)
        self.portfolio = self.get_portfolio()
        self.portfolio_trades = self.get_portfolio_trades()
        self.trade_instructions = self.allocate_trades()
        # self.post_portfolio = self.set_post_trade_portfolio()

    def get_model(self):
        return Model(self.trade_request.model_request)

    def get_portfolio(self):
        return Portfolio(self.trade_request.portfolio_request, self.prices.prices)

    def get_portfolio_trades(self):
        return TradeCalculator(self.portfolio, self.model, self.prices.prices)

    def get_prices(self):
        prices = PriceRetriever(self.raw_request)
        prices()
        return prices

    def allocate_trades(self):
        allocation_controller = AllocationController(self.portfolio, self.portfolio_trades)
        instructions_object = allocation_controller.allocate_trades()
        instructions_object.prepare_for_transmission()
        return instructions_object.instructions

    def set_post_trade_portfolio(self):
        return PostTradePortfolio(self.trade_instructions, self.trade_request.portfolio_request, self.prices.prices)


class RawRequest(object):
    def __init__(self, file_type_label=None, file_path=None):
        self.file_type_label = file_type_label
        self.file_path = file_path
        # todo the next three lines are to get it to work at the console. need to fix
        # print(os.getcwd() + file_path)
        # print('C:\/Users\/Rye\/Projects\/Python\/PortMgr\/TradeManager\/test\/test_data\/sheets\/sell_buy\/all_methods_1.xlsx', '\n')
        # self.file_path = 'C:\/Users\/Rye\/Projects\/Python\/PortMgr\/TradeManager\/test\/test_data\/sheets\/sell_buy\/all_methods_1.xlsx'
        self._route_trade_request_type()
        if 'test' in self.file_type_label:
            pass
        else:
            self._validate_raw_request()

    def _route_trade_request_type(self):
        """
        Determines what file type the trade request was received in and routes to the appropriate opener.
        """
        try:
            self.raw_request = pd.DataFrame(self.file_path)
        except Exception:
            if 'xl' in self.file_type_label:
                # todo add conditional that checks for model tab in sheet
                # todo handle blank rows in between positions
                self.raw_request = pd.read_excel(self.file_path, engine='xlrd')
                # self.raw_request['symbol'].astype("int")
            elif 'csv' in self.file_type_label:
                self.raw_request = pd.read_csv(self.file_path)
            elif 'json' in self.file_type_label:
                self.raw_request = pd.read_json(self.file_path)
                # todo must transform into pandas
            elif 'txt' in self.file_type_label:
                pass  # todo
            elif 'test' in self.file_type_label:
                # FOR TESTING ONLY, Must be object that can make a dataframe.
                # structure {data: {'symbol': 'abs'}, 'index': ['model']}
                if 'index' in self.file_path:
                    self.raw_request = pd.DataFrame(self.file_path['data'], index=self.file_path['index'])
                else: self.raw_request = pd.DataFrame(self.file_path['data'])
            else:
                return Exception

    def _validate_raw_request(self):
        self._empty_request()
        self._missing_required_columns()
        self.strip_all()
        self._no_accounts()
        self.raw_request['account_number'] = self.raw_request['account_number'].str.strip()
        self._model_rows_validation()
        self._account_rows_validation()

    def strip_all(self):
        for column in self.raw_request:
            if not is_numeric_dtype(self.raw_request[column]):
                self.raw_request[column] = self.raw_request[column].str.strip()

    def _empty_request(self):
        if self.raw_request.empty:
            raise RuntimeError('Your request was had no data.')

    def _missing_required_columns(self):
        required_columns = ['price', 'account_number', 'symbol', 'model_weight', 'shares', 'restrictions']
        error = []
        for label in required_columns:
            if label not in self.raw_request.columns:
                error.append(label)
        if len(error) > 0:
            raise RuntimeError('The following columns were missing: {}'.format(error))

    def _no_accounts(self):
        if len(self.raw_request.loc[self.raw_request['account_number'] != 'model']) < 1:
            raise RuntimeError('No accounts were found in your request.')

    def _model_rows_validation(self):
        def weights(row):
            runerror = RuntimeError("Model Row Error")
            if not row.model_weight:
                runerror.test_error_code = "BlankWeight"
                raise runerror
            if isinstance(row.model_weight, str):
                if not row.model_weight.isnumeric():
                    runerror.test_error_code = "NonNumericWeight"
                    raise runerror
            if isinstance(row.shares, Number):
                if not math.isnan(row.shares):
                    runerror.test_error_code = "ShareQuantityOnModelLine"
                    raise runerror
            if isinstance(row.shares, str):
                if row.shares.isnumeric():
                    runerror.test_error_code = "ShareQuantityOnModelLine"
                    raise runerror
                try:
                    float(row.shares)
                    runerror.test_error_code = "ShareQuantityOnModelLine"
                    raise runerror
                except ValueError:
                    pass
        self.raw_request[self.raw_request.loc[:,'account_number'] == 'model'].apply(weights, axis=1)

    def _account_rows_validation(self):
        def shares(row):
            runerror = RuntimeError("Account Row Error")
            if not row.shares:
                runerror.test_error_code = "BlankShares"
                raise runerror
            if isinstance(row.shares, str):
                if not row.shares.isnumeric():
                    runerror.test_error_code = "NonNumericShares"
                    raise runerror
            if isinstance(row.model_weight, Number):
                if not math.isnan(row.model_weight):
                    runerror.test_error_code = "WeightOnAccountLine"
                    raise runerror
            if isinstance(row.model_weight, str):
                if row.model_weight.isnumeric():
                    runerror.test_error_code = "WeightOnAccountLine"
                    raise runerror
                try:
                    float(row.model_weight)
                    runerror.test_error_code = "WeightOnAccountLine"
                    raise runerror
                except ValueError:
                    pass


        # todo check if duplicate symbols for an account exist

        self.raw_request[self.raw_request.loc[:,'account_number'] != 'model'].apply(shares, axis=1)

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class TradeRequest(object):
    def __init__(self, raw_request):
        """ Return a Trade Request.
        Args:
        :param raw_request: (RawRequest)
        """
        self.raw_request = raw_request.raw_request
        self.error = []
        self._set_trade_request()


    # todo we need to add method _get_accounts_from_AccountStore and incorporate
    # todo check every account has 'account_cash' plug. Another idea is to allow the user to specify 'cash' or some other token in the restrictions column. Unfortunately either way this hobbles user from being able to copy and paste holdings into an upload sheet and send. Or we keep a list of cash vehicle names. But if they don't provide cash then we assume its zero.

    def _set_portfolio_request(self):
        try:
            self.portfolio_request = self.raw_request.loc[self.raw_request['account_number'] != 'model', ['account_number','symbol', 'shares', 'restrictions']]
        except KeyError as error:
            raise RuntimeError('Trade request must contain a portfolio request object. Yours did not') from error

    def _set_model_request(self):
        if self.raw_request.loc[self.raw_request['account_number'] == 'model'].empty:
            self.model_request = pd.DataFrame()
        else:
            self.model_request = self.raw_request.loc[self.raw_request['account_number'] == 'model', ['symbol', 'model_weight']].set_index(['symbol'])
            self.model_request.columns = ['model_weight']

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
    def __init__(self, model_request=None, *args):
            self.model_request = model_request
            if args:
                if args[0] != 'test':
                    pass
            else:
                self._set_model_positions()

    def _set_model_positions(self):
        if self.model_request.empty:
            self.model_positions = pd.DataFrame({"symbol": 'placeholder', "model_weight": 0}, index=['account_cash'])
            self.model_positions.set_index(['symbol'], inplace=True)
            self.model_positions.drop(['placeholder'], inplace=True)
        else:
            self.model_positions = self.model_request
            if self.model_positions.index.isin(['account_cash']).any():
                self.model_positions.drop(['account_cash'], inplace=True)

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class PriceRetriever(object):
    def __init__(self, raw_request):
        """
        Returns empty PriceRetriever object.
        :param raw_request: pandas dataframe object contains all symbols
        """
        self.error = []
        self.raw_request = raw_request.raw_request


    def __call__(self, test=False, file_name=None, test_array_index=0):
        self._prices_are_numbers()
        self._check_duplicate_user_input_prices()
        retrieval_list = self._set_symbol_retrieval_list()
        if test:
            if file_name:
                remote_prices = self._test_set_remote_prices(retrieval_list, file_name, test_array_index)
            else:
                remote_prices = self._test_set_remote_prices(retrieval_list)
        else:
            remote_prices = self._set_remote_prices(retrieval_list)
        self._combine_local_remote_prices(remote_prices)
        self._flag_no_price()

    def _check_duplicate_user_input_prices(self):
        duplicates = self.raw_request[self.raw_request.duplicated(['symbol'], keep=False)].dropna(subset=['price'])
        dup_price_error = pd.DataFrame()
        for name, group in duplicates.groupby('symbol'):
            if len(group) > 1:
                dup_price_error = dup_price_error.append(group, ignore_index=True)
        if len(dup_price_error) > 0:
            raise ValueError(dup_price_error.to_string())

    def _prices_are_numbers(self):
        if self.raw_request['price'].fillna(0).dtype == 'object':
            raise ValueError('Non numeric price entered.')

    def _set_symbol_retrieval_list(self):
        """
        Creates the list of symbols to retrieve from third party price provider.
        :return: none
        """
        symbols_only = self.raw_request[self.raw_request.loc[:,'symbol'].notnull()].copy()
        symbols_only['symbol'] = symbols_only.loc[:,'symbol'].astype(str)
        symbols_only = symbols_only[~symbols_only.loc[:,'symbol'].str.contains('accountstore', case=False)]
        symbols_only = symbols_only[~symbols_only.loc[:, 'symbol'].str.contains('account_cash', case=False)]
        grouped_symbols = symbols_only.groupby('symbol')
        for_retrieval = pd.DataFrame()
        for name, group in grouped_symbols:
            if len(group) == 1:
                for_retrieval = for_retrieval.append(group[group.loc[:,'price'].isnull()])
            elif group.loc[:, 'price'].isnull().all():
                for_retrieval = for_retrieval.append(group.drop_duplicates(['symbol']))
        return pd.DataFrame(index=for_retrieval['symbol'].unique(), columns=['price']) if for_retrieval.size != 0 else pd.DataFrame()

    def _set_remote_prices(self, retrieval_list):
        for symbol in retrieval_list:
            try:
                yahoo = Share(symbol=symbol)
                price = yahoo.get_price()
                retrieval_list.set_value(symbol, 'price', price)
            except (AttributeError, TypeError) as e:
                self.error.append( {symbol, 'Invalid symbol. Check for spaces or other non-alphanumeric characters'})
        return retrieval_list

    def _test_set_remote_prices(self, retrieval_list, file_name=None, test_array_index=0):
        """
        For testing only.
        :param file_name: string, path to file
        :param test_array_index: int, position of test data in the array test data objects
        :return: none
        """
        if file_name:
            import json
            with open(file_name, 'r') as ob:
                test_object = json.load(ob)
                return pd.DataFrame(test_object[test_array_index]).set_index(['symbol'])
        else:
            for symbol in retrieval_list.index:
                retrieval_list.set_value(symbol, 'price', 50)
            return retrieval_list

    def _combine_local_remote_prices(self, remote_prices):
        """
        :return: none
        """
        local = self.raw_request.loc[:,['symbol', 'price']].dropna().set_index(['symbol'])
        self.prices = pd.concat([remote_prices, local]).astype(float)

    def _flag_no_price(self):
        no_price = self.prices.loc[self.prices['price'].isnull()]
        if len(no_price):
            raise RuntimeError(no_price.to_string())

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])

if __name__ == "__main__": # pass
    file_type = 'xl'
    path = os.getcwd() + '\/test\/test_data\/sheets\/sell_buy\/all_methods_3.xlsx'
    trade_manager = TradeManager(file_type, path)
    # print(trade_manager.trade_instructions)
    # trade_manager = TradeManager(file_type='json', path={"account_number": ["gt056"], "symbol": ["account_cash"], "model_weight": None, "shares": 45,"price": '50', "restrictions": None})
    # trade_manager = TradeManager('json', json.dumps({"account_number": ["model","gt056"], "symbol": ["ABC","account_cash"], "model_weight": [0.01,None], "shares": [None, 5000], "price": ['50',1],"restrictions": None}))