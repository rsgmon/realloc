import pandas as pd
import numpy as np

class Portfolio(object):
    def __init__(self, portfolio_request, prices):
        """
        Returns a portfolio object
        :param portfolio_request: dataframe containing accounts, positions, and restrictions.
        :param prices: dataframe containing symbols and prices 
        """
        self.portfolio_request = portfolio_request
        self.prices = prices
        self.account_numbers = self.portfolio_request['account_number'].unique()
        self._assemble_accounts()
        self.set_portfolio_positions_and_value()
        self._account_position_matrix = self.create_account_matrix()
        self.create_cash_matrix()

    def _assemble_accounts(self):
        """
            sets self.accounts to list of account objects.
        """
        self.accounts = []
        for account in self.account_numbers:
            self.accounts.append(Account(self.portfolio_request[self.portfolio_request.loc[:, 'account_number'] == account]))

    def _aggregate_share_positions(self):
        """
        Creates a single dataframe of account positions grouped by symbol.
        :return: dataframe
        """
        portfolio_concatenated_positions = pd.DataFrame()
        for account in self.accounts:
            portfolio_concatenated_positions = pd.concat([portfolio_concatenated_positions, account.account_positions])
        return portfolio_concatenated_positions.groupby(portfolio_concatenated_positions.index).agg(np.sum)

    def set_portfolio_cash(self):
        self.portfolio_cash = 0
        for account in self.accounts:
            self.portfolio_cash +=(account.account_cash.loc['account_cash', 'shares'])

    def set_portfolio_positions_and_value(self):
        """
        Sets attribute portfolio_positions to have aggregated positions
        :return: none
        """
        self.portfolio_positions = self._aggregate_share_positions()
        self.set_portfolio_cash()
        if len(self.portfolio_positions) > 0:
            self.portfolio_positions['price'] = self.prices
            self.portfolio_positions['position'] = self.portfolio_positions['shares']* self.portfolio_positions['price']
            self.portfolio_value = round(self.portfolio_positions['position'].sum() + self.portfolio_cash, 2)
            self.portfolio_positions['portfolio_weight'] = self.portfolio_positions['position']/self.portfolio_value
        else:
            self.portfolio_positions= pd.DataFrame(columns=['shares', 'price','position', 'portfolio_weight'])
            self.portfolio_value = self.portfolio_cash

    def create_cash_matrix(self):
        self._cash_matrix = pd.DataFrame()
        for account in self.accounts:
            self._cash_matrix = pd.concat([self._cash_matrix, pd.DataFrame([account.account_cash.loc['account_cash',:]['shares']], index=account.account_number)])
        self._cash_matrix.columns=['cash']


    def create_account_matrix(self):
        account_matrix = pd.DataFrame()
        for account in self.accounts:
            account_copy = account.account_positions.copy()
            account_copy.columns=account.account_number
            account_matrix = pd.concat([account_matrix, account_copy], axis=1)
        return account_matrix.fillna(0)


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
        self.account_number = self.account_raw['account_number'].unique()
        self.account_positions = self.account_raw.loc[self.account_raw.loc[:, 'symbol'] != 'account_cash'].dropna(subset=['symbol']).drop(['restrictions', 'account_number'], 1).set_index(
            ['symbol'])
        self.account_cash = self.account_raw.loc[self.account_raw.loc[:, 'symbol'] == 'account_cash'].dropna(
            subset=['symbol']).drop(['restrictions', 'account_number'], 1).set_index(
            ['symbol'])
        self.account_level_restrictions = self.account_raw.dropna(subset=['restrictions']).drop(['symbol', 'shares'], 1)

        # todo self.position_level_restrcitions



    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])