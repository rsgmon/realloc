import math
import pandas as pd

from numbers import Number
from pandas.api.types import is_numeric_dtype

from .allocation import AllocationController
from .portfolio import Portfolio, PostTradePortfolio
from .trade_calculator import TradeCalculator


def is_number(x):
    try:
        price = int(x)
    except ValueError:
        return False
    return True


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

    def allocate_trades(self):
        allocation_controller = AllocationController(self.portfolio, self.portfolio_trades)
        instructions_object = allocation_controller.allocate_trades()
        instructions_object.prepare_for_transmission()
        return instructions_object.instructions

    def set_post_trade_portfolio(self):
        return PostTradePortfolio(self.trade_instructions, self.trade_request.portfolio_request, self.prices.prices)

    def get_prices(self):
        prices = Prices(self.raw_request)
        return prices


class RawRequest(object):
    def __init__(self, file_type_label=None, file_path=None, test=False):
        self.file_type_label = file_type_label
        self.file_path = file_path
        # todo the next three lines are to get it to work at the console. need to fix
        # print(os.getcwd() + file_path)
        # print('C:\/Users\/Rye\/Projects\/Python\/PortMgr\/TradeManager\/test\/test_data\/sheets\/sell_buy\/all_methods_1.xlsx', '\n')
        # self.file_path = 'C:\/Users\/Rye\/Projects\/Python\/PortMgr\/TradeManager\/test\/test_data\/sheets\/sell_buy\/all_methods_1.xlsx'
        self._route_trade_request_type()
        if test:
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
        self._strip_all()
        self._no_accounts()
        self._has_price()
        self._duplicate_price()
        self._has_account_cash()
        self.raw_request['account_number'] = self.raw_request['account_number'].str.strip()
        self._model_rows_validation()
        self._account_rows_validation()

    def _has_account_cash(self):
        accounts = []
        for i, v in self.raw_request.groupby(['account_number']):
            if i == 'model': continue
            if v[v.loc[:,'symbol'] == 'account_cash'].shape[0] != 1:
                accounts.append(i)
        if accounts:
            raise RuntimeError('The following accounts do not have an account_cash entry {0}'.format(','.join(accounts)))

    def _strip_all(self):
        for column in self.raw_request:
            if not is_numeric_dtype(self.raw_request[column]):
                self.raw_request[column] = self.raw_request[column].astype('str')
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

    def _has_price(self):
        raw_request_prices_with_numbers = self.raw_request[self.raw_request['price'].apply(is_number)]
        raw_request_prices_with_numbers['price'] = raw_request_prices_with_numbers['price'].astype(float)
        sum_prices = raw_request_prices_with_numbers.groupby(['symbol']).sum()
        # sum_prices.drop(['account_cash'], inplace=True)
        if (sum_prices.price == 0).any():
            missing_price_symbols = sum_prices[sum_prices.loc[:,'price'] == 0].index.values
            raise RuntimeError('The following symbols are missing prices. {0}'.format(missing_price_symbols))


    def _duplicate_price(self):
        groups = self.raw_request.groupby(['symbol'])
        dupes_not_equal_price = []
        for i,v in groups:
            prices = []
            for value in v.price.values:
                try:
                    price = int(value)
                except ValueError:
                    continue
                prices.append(price)
            if len(set(prices)) > 1:
                dupes_not_equal_price.append(i)
            if dupes_not_equal_price:
                raise RuntimeError('The following symbols have two different prices. {0}'.format(dupes_not_equal_price))


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


class Prices(object):
    def __init__(self, raw_request, test=False):
        """
        Returns empty Prices object.
        :param raw_request: pandas dataframe object contains all symbols
        """
        self.error = []
        self.raw_request = raw_request.raw_request.loc[:,['symbol','price']]
        if test:
            pass
        else:
            self._set_prices()

    def fill_na(self, prices):
        if isinstance(prices, list):
            for price in prices:
                try:
                    price = int(price)
                except ValueError:
                    price = float('NaN')
        else:
            try:
                int(prices)
            except ValueError:
                return float('NaN')
            return prices


    def fill_na_or_string_prices(self):
        self.raw_request['price'] = self.raw_request['price'].apply(self.fill_na)

    def _set_prices(self):
        self.fill_na_or_string_prices()
        self._prices_are_numbers()
        self.prices = self._filter_prices().set_index(['symbol'])

    def _filter_prices(self):
        prices = self.raw_request.dropna(subset=['price']).drop_duplicates()
        return prices.drop(prices.loc[prices['symbol'] == "account_cash"].index)

    def _prices_are_numbers(self):
        if self.raw_request['price'].fillna(0).dtype == 'object':
            raise ValueError('Non numeric price entered.')


    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


