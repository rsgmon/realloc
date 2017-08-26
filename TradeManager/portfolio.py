import pandas as pd
import numpy as np

class Portfolio(object):
    def __init__(self, portfolio_request, prices, *args):
        """
        Returns a portfolio object
        :param portfolio_request: dataframe containing accounts, positions, and restrictions.
        :param prices: dataframe containing symbols and prices
        :param args: only for testing, can be any string and prevents some init
        """
        self.portfolio_request = portfolio_request
        self.prices = prices
        self.account_numbers = self.portfolio_request['account_number'].unique()
        if len(args) == 0:
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
        return portfolio_concatenated_positions.groupby(level=0).sum()

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
            account_matrix = pd.concat([account_matrix, account.account_positions])
        return account_matrix

    @property
    def account_matrix(self):
        return self._account_position_matrix

    @property
    def cash_matrix(self):
        return self._cash_matrix

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])

class PostTradePortfolio(Portfolio):
    def __init__(self, trade_instructions, portfolio_request, prices):
        Portfolio.__init__(self, portfolio_request, prices)
        self.update_accounts(trade_instructions)

    def update_accounts(self, trade_instructions):
        for number in self.account_numbers:
            cash_change = trade_instructions.copy()
            cash_change['cash_change'] = (cash_change['shares'] * self.prices.price)
            account_trade_instructions = cash_change.groupby('account').get_group(number)
            for account in self.accounts:
                if account.account_number[0] == number:
                    account.update_account(account_trade_instructions)
        self.set_portfolio_positions_and_value()
        self._account_position_matrix = self.create_account_matrix()
        self.create_cash_matrix()


class Account(object):
    def __init__(self, request):
        self.account_raw = request
        self.account_number = self.account_raw['account_number'].unique()
        self.account_positions = self.account_raw.loc[self.account_raw.loc[:, 'symbol'] != 'account_cash'].dropna(subset=['symbol']).drop(['restrictions'], 1).set_index(['symbol', 'account_number'])
        self.account_cash = self.account_raw.loc[self.account_raw.loc[:, 'symbol'] == 'account_cash'].dropna(
            subset=['symbol']).drop(['restrictions', 'account_number'], 1).set_index(
            ['symbol'])
        self.account_level_restrictions = self.account_raw.dropna(subset=['restrictions']).drop(['symbol', 'shares'], 1)

        # todo self.position_level_restrcitions

    def update_account(self, trades):
        self.update_cash(trades)
        self.update_positions(trades)

    def update_cash(self, trades):
        self.account_cash.set_value('account_cash', 'shares', self.account_cash.loc['account_cash', 'shares'] - trades['cash_change'].sum())

    def update_positions(self, trades):
        self.account_positions = pd.concat([self.account_positions, pd.DataFrame(trades['shares'])]).groupby(level=0).sum()




    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])