import pandas as pd
import numpy as np
import json

class Portfolio(object):
    def __init__(self, account_instructions):
        self.account_instructions = account_instructions
        self.accounts = self._get_accounts_from_brokers(self.account_instructions)
        # self.concatenated_positions = self.concat_positions()
        # self.aggregated_portfolio = self.aggregate_share_positions()
        # self.portfolio_value = self.get_portfolio_value(self.aggregated_portfolio)

    def _get_accounts_from_brokers(self, account_instructions ):
        if not isinstance(account_instructions, list):
            account_instructions = [account_instructions]
        accounts_from_broker = []
        for instruction in account_instructions:
            with open(instruction, 'r') as account:
                account = json.loads(account.read())
            accounts_from_broker.append(account)
        return accounts_from_broker

    def _pandaize_positions(self, accounts=None):
        accounts = accounts if accounts else self.accounts
        portfolio_accounts = []
        for account in accounts:
            portfolio_accounts.append(pd.DataFrame(account['account_positions']))
        portfolio_level_positions = pd.concat(portfolio_accounts, axis=1).fillna(0)
        return portfolio_level_positions

    def _aggregate_share_positions(self):
        portfolio_concatenated_positions = pd.DataFrame()
        for account in self.accounts:
            portfolio_concatenated_positions = pd.concat([portfolio_concatenated_positions,
                                                   pd.DataFrame(account['account_positions'])])
        grouped_portfolio_positions = portfolio_concatenated_positions.groupby('symbol').agg(np.sum)
        del grouped_portfolio_positions['price']
        portfolio_concatenated_positions.set_index('symbol',inplace=True)
        price_matrix = portfolio_concatenated_positions['price']
        price_matrix.drop_duplicates(inplace=True)
        portfolio_positions = pd.concat([grouped_portfolio_positions, price_matrix], axis=1)
        portfolio_positions['position'] = portfolio_positions['shares']* portfolio_positions['price']
        portfolio_positions['portfolio_weight'] = portfolio_positions['position']/portfolio_positions['position'].sum()
        return portfolio_positions

    def get_portfolio_value(self, portfolio_positions):
        return portfolio_positions['position'].sum()