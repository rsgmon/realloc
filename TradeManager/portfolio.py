import pandas as pd
import numpy as np
import json

class Portfolio(object):
    def __init__(self, portfolio_request=None):
        if portfolio_request:
            self.portfolio_request = portfolio_request
            self.portfolio = self.get_portfolio_positions(self.portfolio_request)
            self.portfolio_value = self.get_portfolio_value(self.portfolio_request)
            self.account_matrix = self.create_account_matrix(self.portfolio_request)

    def _assemble_accounts(self, portfolio_request):
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
        return portfolio_concatenated_positions

    def _clean_aggregated_positions(self, aggregated_position):
        price_matrix = self._create_price_matrix(aggregated_position)
        grouped_portfolio_positions = aggregated_position.groupby('symbol').agg(np.sum)
        del grouped_portfolio_positions['price']
        portfolio_positions = pd.concat([grouped_portfolio_positions, price_matrix], axis=1)
        portfolio_positions['position'] = portfolio_positions['shares']* portfolio_positions['price']
        portfolio_positions['portfolio_weight'] = portfolio_positions['position']/portfolio_positions['position'].sum()
        return portfolio_positions

    def _create_price_matrix(self, aggregated_position):
        price_matrix = aggregated_position.copy(deep=True)
        price_matrix.drop_duplicates(inplace=True, subset='symbol')
        price_matrix.set_index('symbol', inplace=True)
        del price_matrix['shares']
        return price_matrix

    def get_portfolio_value(self, account_instructions):
        cleaned_positions = self.get_portfolio_positions(account_instructions)
        return cleaned_positions['position'].sum()

    def get_portfolio_positions(self, portfolio_request):
        raw_accounts = self._assemble_accounts(portfolio_request)
        validated_accounts = self._validate_accounts(raw_accounts)
        aggregated_positions = self._aggregate_share_positions(validated_accounts)
        cleaned_positions = self._clean_aggregated_positions(aggregated_positions)
        return cleaned_positions

    def create_account_matrix(self, portfolio_request):
        accounts = self._assemble_accounts(portfolio_request)
        account_matrix = pd.DataFrame()
        for account in accounts:
            pdaccount = pd.DataFrame(account['account_positions']).set_index('symbol')
            pdaccount.rename(columns={'shares': account['account_number']}, inplace=True, )
            account_matrix = pd.concat([account_matrix, pdaccount], axis=1)
        del account_matrix['price']
        return account_matrix.fillna(0)