import pandas as pd
import numpy as np
import json
from TradeManager.test.test_data.test_data import prices

class Portfolio(object):
    def __init__(self, portfolio_request=None):
        """
        :param portfolio_request: dict that is usually a member of a TradeRequest object.
        """
        if portfolio_request:
            self.portfolio_request = portfolio_request
            self._get_account_number_list()
            self._portfolio = self.get_portfolio_positions(self.portfolio_request)
            self._portfolio_value = self.get_portfolio_value(self.portfolio_request)
            self._account_matrix = self.create_account_matrix(self.portfolio_request)
            self._cash_matrix = self.get_cash_matrix()

    def _assemble_accounts(self, portfolio_request):
        """
            :param portfolio_request: dict that is usually a member of a TradeRequest object.
        """
        accounts = []
        if 'account_instructions' in portfolio_request:
            if portfolio_request['account_instructions']:
                for broker_account in self._get_accounts_from_brokers(portfolio_request['account_instructions']):
                    accounts.append(broker_account)
        if 'raw_accounts' in portfolio_request:
            if portfolio_request['raw_accounts']:
                for user_account in portfolio_request['raw_accounts']:
                    accounts.append(user_account)
        return accounts

    def _validate_accounts(self, accounts):
        #this method needs futher work but is here a placeholder to remember that
        return accounts

    def _get_accounts_from_brokers(self, account_instructions ):
        if not isinstance(account_instructions, list):
            account_instructions = [account_instructions]
        accounts_from_broker = []
        for instruction in account_instructions:
            with open(instruction, 'r') as account:
                account = json.loads(account.read())
            accounts_from_broker.append(account)
        return accounts_from_broker

    def _aggregate_share_positions(self, accounts):
        portfolio_concatenated_positions = pd.DataFrame()
        for account in accounts:
            portfolio_concatenated_positions = pd.concat([portfolio_concatenated_positions, pd.DataFrame(account['account_positions'])])
        del portfolio_concatenated_positions['price']
        grouped_portfolio_positions = portfolio_concatenated_positions.groupby('symbol').agg(np.sum)
        return grouped_portfolio_positions

    def _clean_aggregated_positions(self, aggregated_position):
        price_matrix = self.get_price_matrix()
        portfolio_positions = pd.concat([aggregated_position, price_matrix], axis=1)
        portfolio_positions['position'] = portfolio_positions['shares']* portfolio_positions['price']
        portfolio_positions['portfolio_weight'] = portfolio_positions['position']/portfolio_positions['position'].sum()
        return portfolio_positions

    def get_price_matrix(self):
        """This is still a very demo version method. I assume I have price list but made it a little more Robust in case I do more testing. I get the prices and then check if that symbol is in the portfolio and delete shares as if I know I wouldn't have shares. In the end when a transaction is initiated all prices will have to be retrieved from some source and that set of prices has to be the 'price source of truth' for that entire transaction."""
        all_prices = pd.DataFrame(prices).set_index('symbol')
        portfolio_prices = pd.concat([self._aggregated_positions, all_prices], axis=1).dropna()
        del portfolio_prices['shares']
        return portfolio_prices

    def get_portfolio_value(self, account_instructions):
        cleaned_positions = self.get_portfolio_positions(account_instructions)
        return cleaned_positions['position'].sum()

    def get_portfolio_positions(self, portfolio_request):
        self._raw_accounts = self._assemble_accounts(portfolio_request)
        self._validated_accounts = self._validate_accounts(self._raw_accounts)
        self._aggregated_positions = self._aggregate_share_positions(self._validated_accounts)
        self._cleaned_positions = self._clean_aggregated_positions(self._aggregated_positions)
        return self._cleaned_positions

    def get_cash_matrix(self):
        return pd.DataFrame(self._account_matrix.loc['cash',:])

    def create_account_matrix(self, portfolio_request):
        accounts = self._assemble_accounts(portfolio_request)
        account_matrix = pd.DataFrame()
        for account in accounts:
            pdaccount = pd.DataFrame(account['account_positions']).set_index('symbol')
            pdaccount.rename(columns={'shares': account['account_number']}, inplace=True, )
            account_matrix = pd.concat([account_matrix, pdaccount], axis=1)
        del account_matrix['price']
        y = account_matrix.fillna(0)
        return account_matrix.fillna(0)


    def _get_account_number_list(self):
        account_numbers = []
        for number in self._assemble_accounts(self.portfolio_request):
            account_numbers.append(number['account_number'])
        self._account_numbers = tuple(account_numbers)

    @property
    def account_numbers(self):
        """Get the account numbers."""
        return self._account_numbers

    @property
    def portfolio_positions(self):
        """Get the portfolio positions."""
        return self._portfolio

    @property
    def portfolio_value(self):
        return self._portfolio_value

    @property
    def account_matrix(self):
        return self._account_matrix

    @property
    def cash_matrix(self):
        return self._cash_matrix