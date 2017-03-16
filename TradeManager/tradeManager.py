import test.test_data
import test.intermediate_test_data
import pandas as pd
import numpy as np
from TradeManager.portfolio import Portfolio


class TradeManager(object):
    def __init__(self, trade_request=None):
        self.trade_request = test.test_data.trade_request
        self.model = self.get_model()
        self.portfolio = self.get_portfolio()
        self.portfolio_trades = self.get_portfolio_trades()
        self.trades_by_account = self.allocate_trades()

    def get_model(self):
        return Model(self.trade_request['model_id'])

    def get_portfolio(self):
        return Portfolio(self.trade_request['account_numbers'])

    def get_portfolio_trades(self):
        return TradeCalculator(self.model.model_positions, self.portfolio)

    def allocate_trades(self):
        return TradeAllocator(self.portfolio, self.portfolio_trades)


class Model(object):
    def __init__(self, model):
        self.model = model
        self.model_positions = self.get_model(self.model)

    def get_model(self, model):
        model = test.test_data.model['model_positions']
        return pd.DataFrame(model).rename(columns={'weight':'model_weight'}).groupby('symbol').agg(np.sum)


class PriceRetriever(object):
    def __init__(self, symbols=None):
        if symbols:
            self.get_prices(symbols)
        else:
            pass

    def get_prices(self, symbols):
        pass


class TradeAllocator(object):
    def __init__(self, portfolio, trade_list):
        self.portfolio = portfolio
        self.trade_list = trade_list

    def construct_trade_account_matrix(self):
        trade_account_matrix = self.trade_list
        for account in self.portfolio.accounts:
            trade_account_matrix = pd.concat([trade_account_matrix, pd.DataFrame(account['account_positions']).set_index('symbol').rename(columns={'position':account['account_number']})], axis=1).fillna(0)
        return trade_account_matrix

    def determine_trades(self, trade_account_matrix):
        trade_account_matrix['sells'] = trade_account_matrix['dollar_trades'].apply(lambda x: 0 if x > 0 else x)

        return trade_account_matrix

class Account(object):
    def __init__(self, account):
        self.account = account

    def get_positions(self):
        pass


