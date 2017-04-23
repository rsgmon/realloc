import pandas as pd
import numpy as np

class TradeAllocator(object):
    def __init__(self, portfolio, trade_list):
        self.portfolio = portfolio
        self.trade_list = trade_list
        self._tam = TradeAccountMatrix(self.account_matrix.portfolio, self.trade_list)

    def allocate_trades(self):
        trade_selector = TradeSelector()
        # while tam_has trades
            # trade = trade_selector
            # update_tam
        trade = trade_selector._select_accounts(self._tam.trade_account_matrix, self.portfolio._account_numbers)
        # self._tam.update_tam(trade)


class TradeAccountMatrix(object):
    def __init__(self, portfolio, trade_list):
        self.portfolio= portfolio
        self.trade_list = trade_list
        self.trade_account_matrix = self._construct_account_trade_matrix(self.portfolio.account_matrix, self.trade_list)

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

    @property
    def trades_remaining(self):
        if sum(self.trade_account_matrix['shares'].nonzero()[0]) == 0:
            return False
        else:
            return True



class TradeSelector(object):
    def __init__(self):
        pass

    def _select_accounts(self, trade_account_matrix, account_numbers):
        tam = trade_account_matrix.copy()
        def my_test(row, account_numbers):
            count = 0
            if row['shares'] < 0:
                count +=1
            for number in account_numbers:
                if row[number] > 0:
                    count += 1
                    acc_number = number
            if count == 2:
                return acc_number
            else: return 0
        tam['trades'] = tam.apply(lambda row: my_test(row, account_numbers), axis=1)
        return tam

    def _remove_non_trade(self, selected_accounts, account_numbers):
        pass #

    def get_trades(self, trade_account_matrix, account_numbers):
        selected_accounts = self._select_accounts(trade_account_matrix, account_numbers)
        ready = self._remove_non_trade(selected_accounts, account_numbers)
        print(selected_accounts)

