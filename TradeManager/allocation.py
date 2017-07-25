import pandas as pd
import numpy as np

class AllocationController(object):
    def __init__(self, portfolio, trade_calculator):
        self.portfolio = portfolio
        self.portfolio_trade_list = trade_calculator.portfolio_trade_list
        self.trade_instructions = TradeInstructions()

    def _select_trade_selector(self):
        if len(self.portfolio.account_numbers) == 1:
            self.trade_selector = SingleAccountTradeSelector(self.portfolio, self.portfolio_trade_list)
            trades = self.trade_selector.create_trades()
        else:
            self.trade_selector = trades = MultipleAccountTradeSelector()
        return trades

    def _deep_copy_object(self):
        pass

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class TradeSelector(object):
    def __init__(self, portfolio, trade_list):
        self.tam = TradeAccountMatrix(portfolio, trade_list)
        self.trade_instructions = TradeInstructions()

    def get_trades(self, trade_account_matrix, account_numbers):
        selected_accounts = self._select_accounts(trade_account_matrix, account_numbers)
        selected_accounts['size'] = self._size_trade(selected_accounts, account_numbers)
        return selected_accounts.apply(self._prepare_for_tam_update, args=[account_numbers], axis=1)

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

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class SingleAccountTradeSelector(TradeSelector):
    def create_trades(self):
        trade_library = TradeLibrary()
        if self._has_sells:
            self.trade_instructions.tradea = trade_library.single_account_sell(self.tam)
        if self._has_buys():
            self._create_buys()

    def _has_buys(self):
        return True

    def _has_sells(self):
        return True

    def _create_sells(self):
        print("single account sells")

    def _create_buys(self):
        print("single account buys")

class MultipleAccountTradeSelector(TradeSelector):
    pass

class TradeAccountMatrix(object):
    def __init__(self, portfolio, portfolio_trade_list):
        self.portfolio_trade_list = portfolio_trade_list
        self.cash = portfolio.cash_matrix.copy()
        self.trade_account_matrix = self._construct_account_trade_matrix(portfolio.account_matrix, self.portfolio_trade_list)

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
        change = trade.loc[:,['trade_account', 'size', 'price']]
        change['cash'] = change.apply(lambda x: round(x['price'] * x['size'],2) if x['size'] > 0 else round(x['price'] * x['size']* -1, 2), axis=1)
        for name, account in change.groupby(['trade_account']):
            account_cash_change = account.loc[:,'cash'].sum()
            self.cash.set_value(name, 'cash', self.cash.loc[name, 'cash'] + account_cash_change)

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


class TradeLibrary(object):
    """This method select accounts for trades with the following constraints. For selling, portfolio has multiple accounts, sell symbols are complete sells that exist in one account."""
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

    def single_account_sell(self, tam):
        return 10



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
        print("new trades added")
        # self._trades = pd.concat([self._trades, new_trade])
