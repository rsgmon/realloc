import pandas as pd
import os
from trade_generator.portfolio import Portfolio, PostTradePortfolio
from trade_generator.trade_calculator import TradeCalculator
from trade_generator.allocation import AllocationController
import math
from numbers import Number
from pandas.api.types import is_numeric_dtype


class TradeManager:
    def __init__(self, file_type=None, path=None):
        """
        Initializes TradeManager to handle trade execution.
        :param file_type: Type of input file.
        :param path: Path to input data.
        """
        self.raw_request = RawRequest(file_type, path)
        self.trade_request = TradeRequest(self.raw_request)
        self.prices = self.get_prices()
        self.model = Model(self.trade_request.model_request)
        self.portfolio = self.get_portfolio()
        self.portfolio_trades = self.get_portfolio_trades()
        self.trade_instructions = self.allocate_trades()

    def get_portfolio(self):
        """ Constructs a Portfolio object from trade request. """
        return Portfolio(self.trade_request.portfolio_request, self.prices.prices)

    def get_portfolio_trades(self):
        """ Computes required trades based on portfolio and model. """
        return TradeCalculator(self.portfolio, self.model, self.prices.prices)

    def allocate_trades(self):
        """ Allocates trades across accounts. """
        allocation_controller = AllocationController(self.portfolio, self.portfolio_trades)
        instructions_object = allocation_controller.allocate_trades()
        instructions_object.prepare_for_transmission()
        return instructions_object.instructions

    def get_prices(self):
        """ Retrieves price data from the raw request. """
        return Prices(self.raw_request)


class RawRequest:
    def __init__(self, file_type_label=None, file_path=None):
        """ Loads raw request data from various file formats. """
        self.file_type_label = file_type_label
        self.file_path = file_path
        self.raw_request = self._load_data()

    def _load_data(self):
        """ Reads input data from supported file formats. """
        try:
            if 'xl' in self.file_type_label:
                return pd.read_excel(self.file_path, engine='openpyxl')
            elif 'csv' in self.file_type_label:
                return pd.read_csv(self.file_path)
            elif 'json' in self.file_type_label:
                return pd.read_json(self.file_path)
            else:
                raise ValueError("Unsupported file type")
        except Exception as e:
            raise RuntimeError(f"Error loading data: {e}")


class TradeRequest:
    def __init__(self, raw_request):
        """ Parses raw request data into structured trade request. """
        self.raw_request = raw_request.raw_request
        self._set_trade_request()

    def _set_trade_request(self):
        """ Extracts portfolio and model request from raw data. """
        self.portfolio_request = self.raw_request[self.raw_request['account_number'] != 'model'][['account_number','symbol', 'shares', 'restrictions']]
        self.model_request = self.raw_request[self.raw_request['account_number'] == 'model'][['symbol', 'model_weight']].set_index(['symbol']) if not self.raw_request[self.raw_request['account_number'] == 'model'].empty else pd.DataFrame()


class Prices:
    def __init__(self, raw_request):
        """ Extracts and validates price data from raw request. """
        self.raw_request = raw_request.raw_request[['symbol', 'price']]
        self._validate_prices()
        self.prices = self._filter_prices().set_index(['symbol'])

    def _validate_prices(self):
        """ Ensures all price values are numeric. """
        if self.raw_request['price'].dtype == 'object':
            raise ValueError('Non-numeric price values detected.')

    def _filter_prices(self):
        """ Filters out invalid or duplicate price entries. """
        prices = self.raw_request.dropna(subset=['price']).drop_duplicates()
        return prices[prices['symbol'] != 'account_cash']


if __name__ == "__main__":
    file_type = 'xl'
    path = os.getcwd() + '/test/test_data/sheets/sell_buy/all_methods_3.xlsx'
    trade_manager = TradeManager(file_type, path)
