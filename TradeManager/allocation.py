import pandas as pd
import numpy as np

class TradeAllocator(object):
    def __init__(self, portfolio, trade_calculator):
        self.portfolio = portfolio
        self.trade_calculator = trade_calculator
        self._tam = TradeAccountMatrix(self.portfolio, self.trade_calculator)

    def allocate_trades(self):
        trade_selector = TradeSelector()
        # The algorithm is right now unimportant. we could attempt to identify trades in the data
        # Or go through a specific algorithm to identify trade types.
        # while tam_has trades
            # trade = trade_selector
            # store trades
            # update_tam
        trade = trade_selector.get_trades(self._tam, self.portfolio.account_numbers)
        trade_instructions = TradeInstructions()
        trade_instructions.trades = trade
        # save new trades (need a persistant object and the trades)
        self._tam.update_tam(trade)
        if self._tam.trades_remaining:
            print('yes')
        else: print('no')
        #if _tam.has_trades then repeat or go to next step.
        # We could (haven't decided) return the trades only or more info like updated portfolio.


class TradeAccountMatrix(object):
    def __init__(self, portfolio, trade_calculator):
        self.portfolio = portfolio
        self.trade_calculator = trade_calculator
        self.cash = portfolio.cash_matrix.copy()
        self.trade_account_matrix = self._construct_account_trade_matrix(self.portfolio.account_matrix, self.trade_calculator.portfolio_trade_list)

    def _construct_account_trade_matrix(self, account_matrix, trade_list):
        # del trade_list['dollar_trades']
        trade_account_matrix = pd.concat([account_matrix, trade_list], axis=1)
        return trade_account_matrix.fillna(0)

    def _remove_trades(self, trade):
        trade['shares'] = 0
        self.trade_account_matrix['shares'].update(trade['shares'])
        return self.trade_account_matrix

    def _remove_holdings(self, trade):
        new_holding= pd.DataFrame()
        def net_holdings(row):
            if pd.isnull(row.iloc[1]):
                return row.iloc[0]
            if row.iloc[0] == abs(row.iloc[1]):
                return 0
            if row.iloc[0] > abs(row.iloc[1]):
                return row.iloc[0] - abs(row.iloc[1])
        for number in self.portfolio.account_numbers:
            update = pd.concat([self.trade_account_matrix[number],trade[number]], axis=1)
            final = update.apply(net_holdings, axis=1)
            self.trade_account_matrix[number] = final

    def _update_cash(self, trade):
        # print(trade)
        change = trade.loc[:,['trade_account', 'size', 'price']]
        change['cash'] = change.apply(lambda x: round(x['price'] * x['size'],2) if x['size'] > 0 else round(x['price'] * x['size']* -1, 2), axis=1)
        for name, account in change.groupby(['trade_account']):
            account_cash_change = account.loc[:,'cash'].sum()
            self.cash.set_value(name, 'cash', self.cash.loc[name, 'cash'] + account_cash_change)
        print(self.cash)


        # def cash_from_trades(row, account_numbers):
        #     for number in account_numbers:
        #         if row[number] != 0:
        #             return [number, row[number]*-1 * row['price']]
        # updated_cash = trade.apply(cash_from_trades, args=[self.portfolio.account_numbers], axis=1).values
        # updated_cash_grid = pd.DataFrame()
        # for account in updated_cash:
        #     updated_cash_grid = pd.concat([updated_cash_grid, pd.Series(account)])
        # updated_cash_grid.columns=['cash']
        # print(updated_cash_grid)
        # print(self.cash)
        # print(updated_cash_grid.groupby(['account']).sum())
        # updated_cash_grid['cash'] = updated_cash_grid[0]
        # self.cash['cash'] += updated_cash_grid['cash']


    def update_tam(self, trade):
        self._remove_trades(trade)
        self._remove_holdings(trade)
        self._update_cash(trade)

    @property
    def trades_remaining(self):
        if sum(self.trade_account_matrix['shares'].nonzero()[0]) == 0:
            return False
        else:
            return True

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class TradeSelector(object):
    def _select_accounts(self, trade_account_matrix, account_numbers):
        tam = trade_account_matrix.trade_account_matrix.copy()
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
        tam['trade_account'] = tam.apply(my_test, args=[account_numbers], axis=1)
        return tam[tam.loc[:,'trade_account'] !=0]

    def _size_trade(self, selected_trades, account_numbers):
        def size_trade(row, account_numbers):
            for number in account_numbers:
                if row[number] > row['shares']:
                    return row['shares']
                else: return row[number]
        return selected_trades.apply(size_trade, args=[account_numbers], axis=1)

    def _prepare_for_tam_update(self, row, account_numbers ):
        for number in account_numbers:
            if row[number] > 0:
                row[number] = row['size']
        return row

    def get_trades(self, trade_account_matrix, account_numbers):
        selected_accounts = self._select_accounts(trade_account_matrix, account_numbers)
        selected_accounts['size'] = self._size_trade(selected_accounts, account_numbers)
        return selected_accounts.apply(self._prepare_for_tam_update, args=[account_numbers], axis=1)

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class SelectorSellMultipleAccounts(TradeSelector):
    def _select_accounts(self, trade_account_matrix, account_numbers):

        # print(trade_account_matrix.trade_account_matrix.loc[(trade_account_matrix.trade_account_matrix.loc[:, account_numbers] > 0).sum(axis=1)==1])
        sells_only = (trade_account_matrix.trade_account_matrix.loc[trade_account_matrix.trade_account_matrix.loc[:, 'shares'] < 0])
        sells_with_multiple_accounts = (sells_only[(sells_only.loc[:, account_numbers] > 0).sum(axis=1) >1])
        sells_with_multiple_accounts
        # print(trade_account_matrix.trade_account_matrix.loc[
        #           (trade_account_matrix.trade_account_matrix.loc[:, account_numbers] > 0).sum(axis=1) == 2])
        # print(trade_account_matrix.trade_account_matrix, '\n', account_numbers, trade_account_matrix.cash)

        # return (trade_account_matrix.cash)

    def _size_trade(self, selected_trades, account_numbers):
        return account_numbers

    def _prepare_for_tam_update(self, row, account_numbers):
        pass


class TradeInstructions(object):
    def __init__(self):
        self._trades = pd.DataFrame()

    @property
    def trades(self):
        return self._trades

    @trades.setter
    def trades(self, new_trade):
        self._trades = pd.concat([self._trades, new_trade])
