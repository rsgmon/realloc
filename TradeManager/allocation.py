import pandas as pd
pd.set_option('display.width', 300)
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
        self.trading_library = TradingLibrary()


    def _has_buys(self):
        return (self.tam.portfolio_trade_list['share_trades'] > 0).any()

    def _has_sells(self):
        return (self.tam.portfolio_trade_list['share_trades'] < 0).any()

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class SingleAccountTradeSelector(TradeSelector):
    def get_trades(self):
        if self._has_sells:
            sell_trades = self.trading_library.single_account_sell(self.tam.trade_account_matrix, self.tam.account_numbers)
            self.trade_instructions.trades = sell_trades
        if self._has_buys():
            buy_trades = self.trading_library.single_account_buy(self.tam.trade_account_matrix, self.tam.account_numbers)
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
        # in the case where the portfolio has not positions we create a model only tam
        portfolio_symbols = pd.Series(account_matrix.index.get_level_values(0).values)
        if not pd.Series(trade_list.index.values).isin(portfolio_symbols).all():
            model_only = self._set_model_only_matrix(trade_list[~trade_list.index.isin(portfolio_symbols)])
            tam = tam.append(model_only)
        #     remove unneeded columns
        tam.drop(['portfolio_weight', 'dollar_trades'], 1, inplace=True)
        return tam

    def _set_model_only_matrix(self, trade_list):
        model_only = trade_list.copy()
        model_only['account_number'] = 'model'
        model_only.set_index([model_only.index, 'account_number'], inplace=True)
        return model_only

    def _update_holdings(self):
        self.trade_account_matrix['shares'] = self.trade_account_matrix['shares'] + self.trade_account_matrix['size']

    def _update_cash(self):
        trade_cash = pd.DataFrame((self.trade_account_matrix['price'] * self.trade_account_matrix['size']).groupby(level=1).sum(), columns=['shares'])
        trade_cash['symbol'] = 'account_cash'
        trade_cash.reset_index().set_index(['symbol', 'account_number'], inplace=True)
        self.cash['shares'] = self.cash['shares'] - trade_cash['shares']

    def _clean_tam(self):
        self.trade_account_matrix.drop(self.trade_account_matrix[self.trade_account_matrix['shares'] == 0].index, inplace=True)
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


class TradingLibrary(object):
    """Other than single_account_sell and single_account_buy, all methods handle multiple accounts."""

    def sell_single_holding(self, tam):
        tam['row_count'] = tam['shares'].groupby(level=0).transform('count')
        tam['select'] = (tam['row_count'] == 1) & (tam['share_trades'] < 0)
        if tam['select'].any():
            tam.drop(['row_count'], 1, inplace=True)
            tam['size'] = tam[tam['select']]['share_trades']
            tam.drop(['select'], 1, inplace=True)
            return True

        else:
            tam.drop(['row_count', 'select'], 1, inplace=True)
            return False

    def single_account_sell(self, tam, ans):
        tam['account'] = ans[0]
        return tam.loc[tam.loc[:,'share_trades'] < 0].loc[:,['shares', 'account']]

    def single_account_buy(self, tam, ans):
        tam['account'] = ans[0]
        return tam.loc[tam.loc[:,'share_trades'] > 0].loc[:,['shares', 'account']]

    def sell_complete(self, tam):
        """
        Select in accounts where model weight is zero for all symbols.
        :param tam:
        :return:
        """
        tam['select'] = tam['model_weight'] == 0
        if tam['select'].any():
            tam['size'] = tam[tam['select']]['shares']
            tam.drop(['select'], 1, inplace=True)
            return True
        else: return False

    def sell_smallest_multiple(self, tam):
        """
        for each symbol find the smallest holding.
            edge case #1: holdings for a given symbol are equal
                if this true use first account in the array
            edge case #2: cash is same for each account (not implemented)
        Selects rows where row count by symbol >1 and share_trades < 0.
        if any rows meet those
            we have trades
            for a given symbol select the account with the smallest holding
            or the first account if two or more accounts have the equally smallest holding.

        :param tam:
        :return:
        """
        tam['over_one'] = ((tam['price'].groupby(level=0).transform('count') > 1) & (tam['share_trades'] < 0))
        if tam['over_one'].any():
            tam['single_min'] = tam.shares.groupby(level=0).transform(lambda x: (~x.duplicated(False)) & (x == x.min()))
            tam['min_all_equal'] = tam.shares.groupby(level=0).transform(lambda x: (x.reset_index().index == 0) & (x.min() == x))
            tam['select'] = (tam['over_one']) & (tam['single_min'] + tam['min_all_equal']) == 1
                # Now we know we have either single minimium for that symbol or the first instance.
            tam['is_entire_holding'] = tam['select'] & (tam['shares'] + tam['share_trades'] < 0)
            tam['entire_holding'] = tam.loc[tam['is_entire_holding'],'shares'] * -1
            tam['entire_holding'].fillna(0, inplace=True)
            tam['is_partial'] = tam['select'] & (tam['shares'] + tam['share_trades'] > 0)
            tam['partial'] = tam.loc[tam['is_partial'],'share_trades']
            tam['partial'].fillna(0, inplace=True)
            tam['size'] = tam['entire_holding'] + tam['partial']
            tam.drop(['min_all_equal','single_min','over_one','select', 'is_entire_holding', 'entire_holding', 'is_partial', 'partial'], axis=1, inplace=True)
            return True
        else:
            tam.drop(['over_one'], axis=1, inplace=True)
            return False

    def buy_single_holding(self, tam, cash):
        tam['row_count'] = tam['price'].groupby(level=0).transform('count')
        tam['select'] = (tam['row_count'] == 1) & (tam['share_trades'] > 0)
        if tam['select'].any():
            tam['dollar_trade'] = tam['share_trades'] * tam['price'] * -1
            tam['cash'] = tam['select'].groupby(level=1).transform(lambda x: cash.loc[x.name,:])
            tam['has_cash'] = (tam['select']) & (tam['cash'] > tam['dollar_trade']*-1)
            if tam['has_cash'].any():
                tam['size'] = tam[tam['has_cash']]['share_trades']
                tam.drop(['dollar_trade', 'cash', 'row_count', 'select', 'has_cash'], 1, inplace=True)
                return True
            else:
                tam.drop(['dollar_trade', 'cash', 'row_count', 'select', 'has_cash'], 1, inplace=True)
                return False
        else:
            tam.drop(['row_count', 'select'], 1, inplace=True)
            return False

    def buy_multiple_holding(self, tam, cash):
        tam['row_count'] = tam['price'].groupby(level=0).transform('count')
        tam['any_trades'] = (tam['row_count'] > 1) & (tam['share_trades'] > 0)
        if tam['any_trades'].any():
            tam['dollar_trade'] = tam['share_trades'] * tam['price']
            tam['cash'] = tam['any_trades'].groupby(level=1).transform(lambda x: cash.loc[x.name, :])
            account = tam.loc[tam.cash == tam.cash.max()].copy()
            for name, testme in tam.groupby(level=1):

            account['min_trade'] = account.loc[:,'dollar_trade'].min()
            account['is_eligible'] = account.loc[:,'cash'] > account.loc[:,'min_trade']
            if account['is_eligible'].any():
                account['eligible'] = account[account['is_eligible']]['dollar_trade']
                account['sum_trades'] = account['eligible'].sum()
                account['sufficient'] = (account['sum_trades'] < account['cash'])
                if ~account['sufficient'].any():
                    account['is_eligible'] = account['eligible'] != account['eligible'].max()
                    account['eligible'] = account[account['is_eligible']]['dollar_trade']
                    account['sum_trades'] = account['eligible'].sum()
                    account['sufficient'] = (account['sum_trades'] < account['cash'])
                tam['select'] = account['is_eligible']
                tam['select'].fillna(False, inplace=True)
                tam['size'] = tam[tam['select']]['share_trades']
                return True
            return False
        return False



class TradeSizeUpdateTamLibrary(object):

    def sell_single_account(self, tam):
        tam['share_trades'] = tam['share_trades'] + tam['size']
        # tam['dollar_trades'] = tam['dollar_trades'] + tam['size'] * tam['price']

    def multiple_update(self, tam):
        # todo dollar trades
        tam['port_buy_size'] = tam['size'].groupby(level=0).transform(lambda x: x.sum() if x.sum() > 0 else 0)
        tam['port_sell_size'] = tam['size'].groupby(level=0).transform(lambda x: x.sum() if x.sum() < 0 else 0)
        tam['share_trades'] = tam['share_trades'] - tam['port_buy_size'] - tam['port_sell_size']
        tam.drop(['port_buy_size', 'port_sell_size'], 1, inplace=True)


class TradeInstructions(object):
    def __init__(self):
        self._trades = pd.DataFrame()

    @property
    def trades(self):
        return self._trades

    @trades.setter
    def trades(self, new_trade):
        self._trades = self._trades.append(new_trade.copy())

