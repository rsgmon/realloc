import pandas as pd
import numpy as np
import json
from TradeManager.test.test_data.test_data import prices


class Portfolio(object):
    def __init__(self, portfolio_request, prices):
        """
        Returns a portfolio object
        :param portfolio_request: dataframe containing accounts, positions, and restrictions.
        :param prices: dataframe containing symbols and prices 
        """
        self.portfolio_request = portfolio_request
        self.prices = prices
        self.account_numbers = self.portfolio_request['account'].unique()
        self._assemble_accounts()
        self.set_portfolio_positions_and_value()
        # self._account_matrix = self.create_account_matrix(self.portfolio_request)
        # self._cash_matrix = self.set_cash_matrix()
        # self._account_position_matrix = self._account_matrix.drop('cash')

    def _assemble_accounts(self):
        """
            :param portfolio_request: dict that is usually a member of a TradeRequest object.
        """
        self.accounts = []
        for account in self.account_numbers:
            self.accounts.append(Account(self.portfolio_request[self.portfolio_request.loc[:, 'account'] == account]))

    def _aggregate_share_positions(self):
        portfolio_concatenated_positions = pd.DataFrame()
        for account in self.accounts:
            portfolio_concatenated_positions = pd.concat([portfolio_concatenated_positions, account.account_positions])
        return portfolio_concatenated_positions.groupby(portfolio_concatenated_positions.index).agg(np.sum)

    def set_portfolio_positions_and_value(self):
        self.portfolio_positions = pd.concat([self._aggregate_share_positions(), self.prices], axis=1)
        self.portfolio_positions['position'] = self.portfolio_positions['shares']* self.portfolio_positions['price']
        self.portfolio_positions['portfolio_weight'] = self.portfolio_positions['position']/self.portfolio_positions['position'].sum()

    def set_cash_matrix(self):
        return pd.DataFrame(self._account_matrix.loc['cash',:])

    def create_account_matrix(self, portfolio_request):
        accounts = self._assemble_accounts(portfolio_request)
        account_matrix = pd.DataFrame()
        for account in accounts:
            pdaccount = pd.DataFrame(account['account_positions']).set_index('symbol')
            pdaccount.rename(columns={'shares': account['account_number']}, inplace=True, )
            account_matrix = pd.concat([account_matrix, pdaccount], axis=1)
        del account_matrix['price']
        return account_matrix.fillna(0)





    @property
    def portfolio_value(self):
        return self._portfolio_value

    @property
    def account_matrix(self):
        return self._account_position_matrix

    @property
    def cash_matrix(self):
        return self._cash_matrix

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])

class Account(object):
    def __init__(self, request):
        self.account_raw = request
        self.account_number = self.account_raw['account'].unique()
        self.account_positions = self.account_raw.loc[self.account_raw.loc[:, 'symbol'] != 'account_cash'].dropna(subset=['symbol']).drop(['restrictions', 'account'], 1).set_index(
            ['symbol'])
        self.account_cash = self.account_raw.loc[self.account_raw.loc[:, 'symbol'] == 'account_cash'].dropna(
            subset=['symbol']).drop(['restrictions', 'account'], 1).set_index(
            ['symbol'])
        self.account_level_restrictions = self.account_raw.dropna(subset=['restrictions']).drop(['symbol', 'shares'], 1)

        # todo self.position_level_restrcitions



    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])