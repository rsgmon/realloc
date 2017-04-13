import pandas as pd
import numpy as np
from TradeManager.portfolio import Portfolio
from TradeManager.trade_calculator import TradeCalculator


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
        return TradeAllocator(self.portfolio, self.portfolio_trades)


class TradeRequest(object):
    def __init__(self, trade_request):
        self.raw_request = trade_request
        self._set_trade_request(trade_request)

    def _set_portfolio_request(self, trade_request):
        if 'portfolio_request' in trade_request:
            portfolio_request = trade_request['portfolio_request']
        else:
            raise Exception('Trade request must contain a portfolio request object. Yours did not')
        if 'account_instructions' not in portfolio_request and 'raw_accounts' not in portfolio_request:
            raise Exception('No account information provided Need account instructions or a raw accounts.')
        return portfolio_request

    def _set_model_request(self, trade_request):
        if 'model_request' in trade_request:
            model_request = trade_request['model_request']
        else:
            raise Exception('Trade request must contain a model request object. Yours did not')
        return self._validate_fields(model_request, 'instructions', 'raw_model')

    def _validate_fields(self, validation_request, instruction, raw):
        if instruction not in validation_request and raw not in validation_request:
            raise Exception('No model provided. You must provide instructions or a raw model.')
        if instruction in validation_request and raw in validation_request:
            if validation_request[instruction] != None and validation_request[raw] != None:
                raise Exception ('You must enter either model instructions or a model but not both.')
        if instruction in validation_request:
            if validation_request[instruction]:
                return validation_request[instruction] # we need to implement the retrieve_model_from_database method
        else:
            return validation_request[raw]

    def _set_trade_request(self, trade_request):
        self.portfolio_request = self._set_portfolio_request(trade_request)
        self.model_request = self._set_model_request(trade_request)
        self.valid_request = {'portfolio_request': self.portfolio_request, 'model_request':self.model_request }


class Model(object):
    def __init__(self, model_request=None):
        if model_request:
            self.model_request = model_request
            self.model_positions = self.get_model_positions(self.model_request)

    def get_model_positions(self, model_request):
        model_positions =  pd.DataFrame(model_request['model_positions'])
        model_positions.set_index('symbol', inplace=True)
        return model_positions


    def retrieve_model_from_database(self):
        pass

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
        pass# trade_account_matrix = self.trade_list
        # for account in self.portfolio:
        #     trade_account_matrix = pd.concat([trade_account_matrix, pd.DataFrame(account['account_positions']).set_index('symbol').rename(columns={'position':account['account_number']})], axis=1).fillna(0)
        # return trade_account_matrix

    def determine_trades(self, trade_account_matrix):
        trade_account_matrix['sells'] = trade_account_matrix['dollar_trades'].apply(lambda x: 0 if x > 0 else x)

        return trade_account_matrix

class Account(object):
    def __init__(self, account):
        self.account = account

    def get_positions(self):
        pass


