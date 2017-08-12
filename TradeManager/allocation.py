import pandas as pd
import numpy as np

class AllocationController(object):
    def __init__(self, portfolio, trade_calculator):
        self.portfolio = portfolio
        self.portfolio_trade_list = trade_calculator.portfolio_trade_list
        self.trade_instructions = TradeInstructions()

    def allocate_trades(self):
        if len(self.portfolio.account_numbers) == 1:
            self.trade_selector = SingleAccountTradeSelector(self.portfolio, self.portfolio_trade_list)
            self.trade_selector.get_trades()
            return self.trade_selector.trade_instructions.trades
        else:
            self.trade_selector = DualAccountTradeSelector(self.portfolio, self.portfolio_trade_list)
            self.trade_selector.get_trades()
            return self.trade_selector.trade_instructions.trades

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class TradeSelector(object):
    def __init__(self, portfolio, trade_list):
        self.tam = TradeAccountMatrix(portfolio, trade_list)
        self.trade_instructions = TradeInstructions()
        self.account_numbers = portfolio.account_numbers
        self.account_selection_library = AccountSelectionLibrary()
        self.trade_sizer = TradeSizingLibrary()


    def _has_buys(self):
        return (self.tam.portfolio_trade_list['dollar_trades'] > 0).any()

    def _has_sells(self):
        return (self.tam.portfolio_trade_list['dollar_trades'] < 0).any()

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class SingleAccountTradeSelector(TradeSelector):
    def get_trades(self):
        if self._has_sells:
            sell_trades = self.account_selection_library.single_account_sell(self.tam.trade_account_matrix.copy(), self.account_numbers)
            self.trade_instructions.trades = sell_trades
        if self._has_buys():
            buy_trades = self.account_selection_library.single_account_buy(self.tam.trade_account_matrix.copy(), self.account_numbers)
            self.trade_instructions.trades = buy_trades


class DualAccountTradeSelector(TradeSelector):
    def get_trades(self):
        if self._has_sells:
            accounts = self.account_selection_library.sell_single_holding(self.tam.trade_account_matrix.copy(), self.account_numbers)
            sizes = self.trade_sizer.sell_single_holding(accounts)
            self.trade_instructions.trades = sizes
            self.tam.update_tam(sizes)


class TradeAccountMatrix(object):
    def __init__(self, portfolio, portfolio_trade_list):
        self.account_numbers = portfolio.account_numbers
        self.portfolio_trade_list = portfolio_trade_list
        self.cash = portfolio.cash_matrix.copy()
        self.trade_account_matrix = self._construct_trade_account_matrix(portfolio.account_matrix, self.portfolio_trade_list)

    def _construct_trade_account_matrix(self, account_matrix, trade_list):
        trade_account_matrix = pd.concat([account_matrix, trade_list], axis=1)
        return trade_account_matrix.fillna(0)

    def _update_trades(self, trade):
        self.trade_account_matrix['shares'].update(self.trade_account_matrix['shares'] - trade['size'])

    def _update_holdings(self, trade):
        new_holding= pd.DataFrame()
        def net_holdings(row):
            if pd.isnull(row.iloc[1]):
                return row.iloc[0]
            if row.iloc[0] == abs(row.iloc[1]):
                return 0
            if row.iloc[0] > abs(row.iloc[1]):
                return row.iloc[0] - abs(row.iloc[1])
        for number in self.account_numbers:
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
        self._update_trades(trade)
        self._update_holdings(trade)
        self._update_cash(trade)

    @property
    def trades_remaining(self):
        if sum(self.trade_account_matrix['shares'].nonzero()[0]) == 0:
            return False
        else:
            return True

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class AccountSelectionLibrary(object):
    """This method select accounts for trades with the following constraints. For selling, portfolio has multiple accounts, sell symbols are complete sells that exist in one account."""
    def sell_single_holding(self, tam, account_numbers):
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

    def single_account_sell(self, tam, account_numbers):
        tam['account'] = account_numbers[0]
        return tam[tam.loc[:,'dollar_trades'] < 0].loc[:,['shares', 'account']]

    def single_account_buy(self, tam, account_numbers):
        tam['account'] = account_numbers[0]
        return tam[tam.loc[:,'dollar_trades'] > 0].loc[:,['shares', 'account']]


class TradeSizingLibrary(object):
    def sell_single_holding(self, selected_trades):
        selected_trades['size'] = selected_trades['shares']
        return selected_trades

    def sell_something(self, selected_trades, account_numbers):
        def size_trade(row, account_numbers):
            for number in account_numbers:
                print(row[number], row['shares'])
                if row[number] > row['shares']:
                    return row['shares']
                else: return row[number]
        return selected_trades.apply(size_trade, args=[account_numbers], axis=1)


class TradeInstructions(object):
    def __init__(self):
        self._trades = pd.DataFrame()

    @property
    def trades(self):
        return self._trades

    @trades.setter
    def trades(self, new_trade):
        self._trades = self._trades.append(new_trade.copy())

