import pandas as pd
import numpy as np

class Portfolio:
    def __init__(self, portfolio_request, prices):
        """
        Initializes a Portfolio object.
        :param portfolio_request: DataFrame containing accounts, positions, and restrictions.
        :param prices: DataFrame containing symbols and prices.
        """
        self.portfolio_request = portfolio_request
        self.prices = prices
        self.account_numbers = self.portfolio_request['account_number'].unique()
        self.accounts = self._assemble_accounts()
        self.set_portfolio_positions_and_value()
        self._account_matrix = self.create_account_matrix()
        self.create_cash_matrix()

    def _assemble_accounts(self):
        """ Creates a list of Account objects from portfolio request. """
        return [Account(self.portfolio_request[self.portfolio_request['account_number'] == acc]) for acc in self.account_numbers]

    def _aggregate_share_positions(self):
        """ Aggregates share positions across all accounts. """
        return pd.concat([account.account_positions for account in self.accounts]).groupby(level=0).sum()

    def set_portfolio_cash(self):
        """ Calculates total portfolio cash. """
        self.portfolio_cash = sum(account.account_cash.get(account.account_number[0], 0) for account in self.accounts)

    def set_portfolio_positions_and_value(self):
        """ Sets aggregated portfolio positions and calculates total value. """
        self.portfolio_positions = self._aggregate_share_positions()
        self.set_portfolio_cash()

        if not self.portfolio_positions.empty:
            self.portfolio_positions['price'] = self.prices.reindex(self.portfolio_positions.index, fill_value=0)
            self.portfolio_positions['position'] = self.portfolio_positions['shares'] * self.portfolio_positions['price']
            self.portfolio_value = round(self.portfolio_positions['position'].sum() + self.portfolio_cash, 2)
            self.portfolio_positions['portfolio_weight'] = self.portfolio_positions['position'] / max(self.portfolio_value, 1)
        else:
            self.portfolio_positions = pd.DataFrame(columns=['shares', 'price', 'position', 'portfolio_weight'])
            self.portfolio_value = self.portfolio_cash

    def create_cash_matrix(self):
        """ Creates a DataFrame tracking cash balances across accounts. """
        self._cash_matrix = pd.concat([account.account_cash for account in self.accounts])

    def create_account_matrix(self):
        """ Creates a DataFrame tracking positions across accounts. """
        return pd.concat([account.account_positions for account in self.accounts])

    @property
    def account_matrix(self):
        return self._account_matrix

    @property
    def cash_matrix(self):
        return self._cash_matrix

    def __str__(self):
        return '\n\n'.join([f'{key}\n{value}' for key, value in self.__dict__.items()])


class Account:
    def __init__(self, request):
        """ Initializes an Account object from a request DataFrame. """
        self.account_raw = request
        self.account_number = self.account_raw['account_number'].unique()[0]
        self.account_positions = (
            self.account_raw[self.account_raw['symbol'] != 'account_cash']
                .dropna(subset=['symbol'])
                .set_index(['symbol', 'account_number'])
        )
        self.account_cash = (
            self.account_raw[self.account_raw['symbol'] == 'account_cash']
                .dropna(subset=['symbol'])
                .set_index(['account_number'])
        )

    def update_account(self, trades):
        """ Updates account positions and cash based on executed trades. """
        self.update_cash(trades)
        self.update_positions(trades)

    def update_cash(self, trades):
        """ Updates cash balance after trades. """
        cash_change = trades.groupby('account_number')['cash_change'].sum()
        self.account_cash.loc[:, 'shares'] -= cash_change.get(self.account_number, 0)

    def update_positions(self, trades):
        """ Updates account positions after trades. """
        new_positions = trades.groupby('symbol')['shares'].sum()
        self.account_positions = self.account_positions.add(new_positions, fill_value=0)

    def __str__(self):
        return '\n\n'.join([f'{key}\n{value}' for key, value in self.__dict__.items()])
