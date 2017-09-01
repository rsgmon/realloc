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
            sell_trades = self.account_selection_library.single_account_sell(self.tam.trade_account_matrix, self.tam.account_numbers)
            self.trade_instructions.trades = sell_trades
        if self._has_buys():
            buy_trades = self.account_selection_library.single_account_buy(self.tam.trade_account_matrix, self.tam.account_numbers)
            self.trade_instructions.trades = buy_trades


class MultipleAccountTradeSelector(TradeSelector):
    def get_trades(self):
        if self._has_sells:
            accounts = self.account_selection_library.sell_single_holding(self.tam.trade_account_matrix, self.tam.account_numbers)
            sizes = self.trade_sizer.sell_single_holding(accounts)
            self.trade_instructions.trades = sizes
            self.tam.update_tam(sizes)
            accounts = self.account_selection_library.sell_single_holding(self.tam.trade_account_matrix, self.tam.account_numbers)


class TradeAccountMatrix(object):

    def __init__(self, portfolio, portfolio_trade_list, *args):
        self.account_numbers = portfolio.account_numbers
        self.account_matrix = portfolio.account_matrix
        self.portfolio_trade_list = portfolio_trade_list
        self.cash = portfolio.cash_matrix.copy()

        if len(args) == 0:
            self.trade_account_matrix = self._construct_trade_account_matrix(self.account_matrix, self.portfolio_trade_list)
            self.trade_account_matrix = self.trade_account_matrix.copy()

    def _construct_trade_account_matrix(self, account_matrix, trade_list):
        tam = account_matrix.join(trade_list)
        portfolio_symbols = pd.Series(account_matrix.index.get_level_values(0).values)
        if not pd.Series(trade_list.index.values).isin(portfolio_symbols).all():
            model_only = self._set_model_only_matrix(trade_list[~trade_list.index.isin(portfolio_symbols)])
            tam = tam.append(model_only)
        tam.drop(['portfolio_weight'], 1, inplace=True)
        return tam

    def _set_model_only_matrix(self, trade_list):
        model_only = trade_list.copy()
        model_only['account_number'] = 'model'
        model_only.set_index([model_only.index, 'account_number'], inplace=True)
        return model_only

    def _update_holdings(self):
        self.trade_account_matrix['shares'] = self.trade_account_matrix['shares'] - self.trade_account_matrix['size']

    def _update_cash(self):
        self.trade_account_matrix['cash'] = self.trade_account_matrix.apply(lambda x: round(x['price'] * x['size'],2) if x['size'] > 0 else round(x['price'] * x['size']* -1, 2), axis=1)
        for name, account in self.trade_account_matrix.groupby(level=1):
            account_cash_change = account['cash'].sum()
            print(account)
            self.cash.set_value(name, 'cash', round(self.cash.loc[name, 'cash'] + account_cash_change),2)


    def _clean_tam(self):
        self.trade_account_matrix.drop(['size'],1, inplace=True)


    def update_tam(self):
        self.trade_account_matrix.fillna(0, inplace=True)
        self._update_holdings()
        self._update_cash()
        self._clean_tam()

    @property
    def trades_remaining(self):
        if sum(self.trade_account_matrix['shares'].nonzero()[0]) == 0:
            return False
        else:
            return True

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class AccountSelectionLibrary(object):
    """Other than single_account_sell and single_account_buy, all methods handle multiple accounts."""

    def sell_single_holding(self, tam):
        tam['row_count'] = tam['shares'].groupby(level=0).transform('count')
        tam['select'] = (tam['row_count'] == 1) & (tam['share_trades'] < 0)
        tam.drop(['row_count'], 1, inplace=True)

    def single_account_sell(self, tam, ans):
        tam['account'] = ans[0]
        return tam.loc[tam.loc[:,'dollar_trades'] < 0].loc[:,['shares', 'account']]

    def single_account_buy(self, tam, ans):
        tam['account'] = ans[0]
        return tam.loc[tam.loc[:,'dollar_trades'] > 0].loc[:,['shares', 'account']]

    def sell_complete(self, tam):
        """
        Select in accounts where model weight is zero for all symbols.
        :param tam:
        :return:
        """
        tam['select'] = tam['model_weight'] == 0


    def sell_smallest_multiple(self, tam):
        """
        tam['accounts >1', tam['sells, tam['smallest holding assuming previous two columns are true, tam['any trues in the last column, tam['there are trues so select trades,
        If tam['select move on the sizing
        else return false

        :param tam:
        :return:
        """

        tam['select'] = ((tam['price'].groupby(level=0).transform('count') > 1) & (tam['share_trades'] < 0) & (tam['shares'] - tam['shares'].groupby(level=0).transform('min') != 0))
        if tam['select'].any():
            tam['is_entire_holding'] = tam['select'] & (tam['shares'] + tam['share_trades'] < 0)
            tam['entire_holding'] = tam.loc[tam['is_entire_holding'],'shares']
            tam['entire_holding'].fillna(0, inplace=True)
            tam['is_partial'] = tam['select'] & (tam['shares'] + tam['share_trades'] > 0)
            tam['partial'] = tam.loc[tam['is_partial'],'shares'] + tam.loc[tam['is_partial'],'share_trades']
            tam['partial'].fillna(0, inplace=True)
            tam['size'] = tam['entire_holding'] + tam['partial']
            tam.drop(['select', 'is_entire_holding', 'entire_holding', 'is_partial', 'partial'], axis=1, inplace=True)
            return True
        else: return False


class TradeSizingLibrary(object):

    def sell_complete(self, tam):
        tam['size'] = tam[tam['select']]['shares']
        return tam


class TradeSizeUpdateTamLibrary(object):

    def sell_single_account(self, tam):
        tam['share_trades'] = tam['share_trades'] + tam['size']
        tam['dollar_trades'] = tam['dollar_trades'] + tam['size'] * tam['price']

    def multiple_update(self, tam):
        # todo dollar trades
        tam['port_trade_size'] = tam['size'].groupby(level=0).transform(lambda x: x.sum() if x.sum() > 0 else 0)
        tam['share_trades'] = tam['share_trades'] + tam['port_trade_size']
        tam.drop(['port_trade_size'], 1, inplace=True)






class TradeInstructions(object):
    def __init__(self):
        self._trades = pd.DataFrame()

    @property
    def trades(self):
        return self._trades

    @trades.setter
    def trades(self, new_trade):
        self._trades = self._trades.append(new_trade.copy())

