import pandas as pd
import numpy as np

class TradeAllocator(object):
    def __init__(self, portfolio, trade_list):
        self.account_matrix = portfolio.account_matrix
        self.trade_list = trade_list
        self._tam = TradeAccountMatrix(self.account_matrix, self.trade_list)

    def allocate_trades(self):
        trade_selector = TradeSelector()
        # while tam_has trades
            # trade = trade_selector
            # update_tam
        trade = trade_selector._select_trades(self._tam.account_matrix, self._tam.trade_list)
        # self._tam.update_tam(trade)


class TradeAccountMatrix(object):
    def __init__(self, portfolio, trade_list):
        self.account_matrix = portfolio.account_matrix
        self.trade_list = trade_list
        self.trade_account_matrix = self._construct_account_trade_matrix(self.account_matrix, self.trade_list)
        self.has_trades_remaining()

    def _construct_account_trade_matrix(self, account_matrix, trade_list):
        del trade_list['dollar_trades']
        trade_account_matrix = pd.concat([account_matrix, trade_list], axis=1)
        return trade_account_matrix.fillna(0)

    def _remove_trades(self, trade):
        trade_to_update = self.trade_account_matrix.loc[trade['symbol'],'shares']
        updated_trade = trade_to_update - trade['amount']
        self.trade_account_matrix.loc[trade['symbol'],'shares'] = updated_trade

    def _remove_holdings(self, trade):
        holding_to_update = self.trade_account_matrix.loc[trade['symbol'],trade['account']]
        updated_holding = holding_to_update + trade['amount']
        self.trade_account_matrix.loc[trade['symbol'],trade['account']] = updated_holding

    def update_tam(self, trade):
        self._remove_trades(trade)
        self._remove_holdings(trade)


    def has_trades_remaining(self):
        if sum(self.trade_account_matrix['shares'].nonzero()[0]) == 0:
            return False
        else:
            return True



class TradeSelector(object):
    def __init__(self):
        pass

    def _select_trades(self, account_matrix, trade_list):
        print(account_matrix, '\n', trade_list)

    def _select_accounts(self, trade_account_matrix):
        tam = trade_account_matrix.copy()
        def my_test(shares, account_1, account_2):
            if shares < 0:
                if account_1 > 0 and account_2 == 0 or account_1 == 0 and account_2 > 0:
                    return True
                else: return False
            else: return False
        tam['testme'] = tam.apply(lambda row: my_test(row['shares'], row.iloc[0], row.iloc[1]), axis=1)
        return tam[tam['testme']]

    def get_trades(self, trade_account_matrix):
        selected_accounts = self._select_accounts(trade_account_matrix)
        print(selected_accounts)

