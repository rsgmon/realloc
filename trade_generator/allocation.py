import pandas as pd
pd.set_option('display.width', 300)
import numpy as np
import math

class AllocationController(object):
    def __init__(self, portfolio, trade_calculator):
        self.portfolio = portfolio
        self.portfolio_trade_list = trade_calculator.portfolio_trade_list
        self.trade_instructions = TradeInstructions()

    def allocate_trades(self):
        if len(self.portfolio.account_numbers) == 1:
            self.trade_selector = SingleAccountTradeSelector(self.portfolio, self.portfolio_trade_list)
            self.trade_selector.get_trades()
            return self.trade_selector.trade_instructions
        else:
            self.trade_selector = MultipleAccountTradeSelector(self.portfolio, self.portfolio_trade_list)
            self.trade_selector.get_trades()
            return self.trade_selector.trade_instructions

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class TradeSelector(object):
    def __init__(self, portfolio, portfolio_trade_list):
        self.trade_account_matrix_object = TradeAccountMatrix(portfolio, portfolio_trade_list)
        self.trade_instructions = TradeInstructions()
        self.trading_library = TradingLibrary()

    def _has_buys(self):
        return (self.trade_account_matrix_object.portfolio_trade_list['share_trades'] > 0).any()

    def _has_sells(self):
        return (self.trade_account_matrix_object.portfolio_trade_list['share_trades'] < 0).any()

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class SingleAccountTradeSelector(TradeSelector):
    def get_trades(self):

        self.trade_account_matrix_object.trade_account_matrix.reset_index(level=['account_number'], inplace=True)
        self.trade_account_matrix_object.trade_account_matrix.account_number = self.trade_account_matrix_object.cash.index[0]
        self.trade_account_matrix_object.trade_account_matrix.set_index(['account_number'], append=True, inplace=True)
        if self.trade_account_matrix_object.trade_account_matrix is None:
            pass
        else:
            if self._has_sells:
                sell_trades = self.trading_library.single_account_sell(self.trade_account_matrix_object.trade_account_matrix, self.trade_account_matrix_object.account_numbers)
                sell_trades['size'] = sell_trades.share_trades
                self.trade_instructions.trades = sell_trades
            if self._has_buys():
                buy_trades = self.trading_library.single_account_buy(self.trade_account_matrix_object.trade_account_matrix, self.trade_account_matrix_object.account_numbers)
                buy_trades['size'] = buy_trades.share_trades
                self.trade_instructions.trades = buy_trades


class MultipleAccountTradeSelector(TradeSelector):
    def get_trades(self):
        if self.trade_account_matrix_object.trade_account_matrix is None:
            pass
        else:
            # if self._has_sells:
            self._get_sell_trades()
            # if self._has_buys():
            self._get_buy_trades()

    def _get_sell_trades(self):
        tam = self.trade_account_matrix_object.trade_account_matrix
        more_trades = True
        if self.trading_library.sell_complete(tam):
            self.trade_instructions.trades = tam
            self.trade_account_matrix_object.update_tam()
            # print('complete_sell', '\n', tam.sort_index(), '\n', self.trade_instructions.trades, '\n')
        while more_trades:
            if self.trading_library.sell_single_holding(tam):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('sell_single', '\n', tam.sort_index(), '\n', self.trade_instructions.trades, '\n', self.trade_account_matrix_object.cash, '\n')
            if self.trading_library.sell_smallest_multiple(tam):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('sell_smallest', '\n', tam.sort_index(), '\n', self.trade_instructions.trades, '\n', self.trade_account_matrix_object.cash, '\n')
            if ~(tam['share_trades'] < 0).any():
                more_trades = False

    def _get_buy_trades(self):
        tam = self.trade_account_matrix_object.trade_account_matrix
        cash = self.trade_account_matrix_object.cash
        more_trades = True
        while more_trades:
            tam_before = tam.copy()
            if self.trading_library.buy_single_holding(tam, cash):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('single_holding', '\n', tam.sort_index(), '\n', self.trade_instructions.trades, '\n')
            while self.trading_library.buy_multiple_entire(tam, cash):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('multi_entire', '\n',  tam.sort_index(),  '\n', self.trade_instructions.trades, '\n')
            if self.trading_library.buy_multiple_partial_one_trade(tam, cash):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('multi_partial', '\n', tam.sort_index(),  '\n', self.trade_instructions.trades, '\n')
            if (tam.equals(tam_before)):
                more_trades = False
        more_trades = True
        while more_trades:
            tam_before = tam.copy()
            while self.trading_library.buy_single_partial(tam, cash):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('single_partial', '\n', tam.sort_index(), '\n', self.trade_instructions.trades, '\n')
            while self.trading_library.buy_new_complete(tam, cash):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('new_complete', '\n', tam.sort_index(), '\n', self.trade_instructions.trades, '\n')
            if self.trading_library.buy_new_partial(tam, cash):
                self.trade_instructions.trades = tam
                self.trade_account_matrix_object.update_tam()
                # print('new_partial', '\n', tam.sort_index(), '\n', self.trade_instructions.trades, '\n', cash)
            if tam.equals(tam_before):
                more_trades = False


class TradeAccountMatrix(object):

    def __init__(self, portfolio, portfolio_trade_list, *args):
        self.account_numbers = portfolio.account_numbers
        self.account_matrix = portfolio.account_matrix
        self.portfolio_trade_list = portfolio_trade_list
        self.cash = portfolio.cash_matrix.copy()
        if portfolio_trade_list is None:
            self.trade_account_matrix = None
        else:
            if len(args) == 0:  #don't know why this xisted. keeping until all tests pass
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
        tam.shares.fillna(0, inplace=True)
        tam.drop(['portfolio_weight', 'dollar_trades'], 1, inplace=True)
        # todo drop any sells with model as account
        return tam

    def _set_model_only_matrix(self, trade_list):
        model_only = trade_list.copy()
        model_only['account_number'] = 'model'
        model_only.set_index([model_only.index, 'account_number'], inplace=True)
        return model_only

    def _update_holdings(self):
        self.trade_account_matrix['shares'] = self.trade_account_matrix['shares'] + self.trade_account_matrix['size']

    def _update_share_trades(self):
        trades_only = (self.trade_account_matrix[self.trade_account_matrix.loc[:, 'size'] != 0]['size']).sum(level=0)
        self.trade_account_matrix['symbols_traded'] = pd.Series(self.trade_account_matrix.index.get_level_values(0)).map(trades_only).fillna(0).values
        self.trade_account_matrix['share_trades'] = self.trade_account_matrix['share_trades'] - self.trade_account_matrix['symbols_traded']
        self.trade_account_matrix.drop(['symbols_traded'], axis=1, inplace=True)

    def _update_cash(self):
        # print(self.cash)
        trade_cash = pd.DataFrame((self.trade_account_matrix['price'] * self.trade_account_matrix['size']).groupby(level=1).sum(), columns=['shares']).round(decimals=2)
        self.cash['update'] = trade_cash
        self.cash.fillna(0, inplace=True)
        self.cash['shares'] = self.cash['shares'] - self.cash['update']
        self.cash.drop(['update'], axis=1, inplace=True)

    def _clean_tam(self):
        self.trade_account_matrix['is_model'] = self.trade_account_matrix.index.get_level_values(level=1) != 'model'
        self.trade_account_matrix.drop(self.trade_account_matrix[(self.trade_account_matrix['shares'] == 0) & self.trade_account_matrix.is_model].index, inplace=True)
        self.trade_account_matrix.drop(['is_model'], 1, inplace=True)
        self.trade_account_matrix.drop(self.trade_account_matrix[self.trade_account_matrix['share_trades'] == 0].index, inplace=True)
        self.trade_account_matrix.drop(['size'],1, inplace=True)

    def update_tam(self):
        self.trade_account_matrix.fillna(0, inplace=True)
        self._update_holdings()
        self._update_share_trades()
        self._update_cash()
        self._clean_tam()

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class TradingLibrary(object):
    """Other than single_account_sell and single_account_buy, all methods handle multiple accounts."""

    def single_account_sell(self, tam, ans):
        tam['account'] = ans[0]
        return tam.loc[tam.loc[:, 'share_trades'] < 0].loc[:, ['share_trades', 'account']]

    def single_account_buy(self, tam, ans):
        tam['account'] = ans[0]
        return tam.loc[tam.loc[:, 'share_trades'] > 0].loc[:, ['share_trades', 'account']]

    def sell_single_holding(self, tam):
        """
        Sells all where there is only one holding of that symbol in the account.
        :param tam:
        :return: bool
        """
        tam['row_count'] = tam['shares'].groupby(level=0).transform('count')
        tam['select'] = (tam['row_count'] == 1) & (tam['share_trades'] < 0) & (tam['shares'] != 0)
        if tam['select'].any():
            tam.drop(['row_count'], 1, inplace=True)
            tam['size'] = tam[tam['select']]['share_trades']
            tam.drop(['select'], 1, inplace=True)
            return True
        else:
            tam.drop(['row_count', 'select'], 1, inplace=True)
            return False

    def sell_complete(self, tam):
        """
        Select in accounts where model weight is zero.
        :param tam:
        :return:
        """
        tam['select'] = tam['model_weight'] == 0
        if tam['select'].any():
            tam['size'] = tam[tam['select']]['shares']*-1
            tam.drop(['select'], 1, inplace=True)
            return True
        else: return False

    def sell_smallest_multiple(self, tam):
        """
        Can generate multiple trades.
        Selects rows where row count by symbol >1 and share_trades < 0.
        if any rows meet those
            we have trades
            for each given symbol select the account with the smallest holding or the first account if two or more accounts have equal holdings.

        :param tam:
        :return:
        """
        tam['over_one'] = ((tam['price'].groupby(level=0).transform('count') > 1) & (tam['share_trades'] < 0))
        if tam['over_one'].any():
            tam['single_min'] = tam.shares.groupby(level=0).transform(lambda x: (~x.duplicated(False)) & (x == x.min()))
            tam['min_all_equal'] = tam.shares.groupby(level=0).transform(lambda x: (x.reset_index().index == 0) & (x.min() == x))
            tam['select'] = (tam['over_one']) & (tam['single_min'] + tam['min_all_equal']) == 1
                # Now we know we have either single minimium for that symbol or the first instance.
            tam['is_entire_holding'] = tam['select'] & (tam['shares'] + tam['share_trades'] <= 0)
            tam['entire_holding'] = tam.loc[tam['is_entire_holding'],'shares'] * -1
            tam['is_partial'] = tam['select'] & (tam['shares'] + tam['share_trades'] > 0)
            tam['partial'] = tam.loc[tam['is_partial'],'share_trades']
            tam['size'] = tam['partial'].fillna(tam['entire_holding'])
            tam.drop(['min_all_equal','single_min','over_one','select', 'is_entire_holding', 'entire_holding', 'is_partial', 'partial'], axis=1, inplace=True)
            return True
        else:
            tam.drop(['over_one'], axis=1, inplace=True)
            return False

    def buy_single_holding(self, tam, cash):
        """
        For any buy in which that symbol has one existing holding and sufficient cash to purchase the entire suggested trade, instruct.
        :param tam: DataFrame
        :param cash: DataFrame
        :return: bool
        """
        tam['row_count'] = tam['price'].groupby(level=0).transform('count')
        tam['select'] = (tam['row_count'] == 1) & (tam['share_trades'] > 0)
        if tam['select'].any():
            tam['dollar_trade'] = tam['share_trades'] * tam['price']
            self.utility_add_cash(tam, cash)
            tam['has_cash'] = (tam['select']) & (tam['cash'] > tam['dollar_trade'])
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

    def buy_multiple_entire(self, tam, cash):
        """This is an alternative to buy_multiple complete. It identifies the highest cash account instruct the largest trade it can.
        :param tam: dataframe
        :param cash: dataframe
        :return: bool
        """
        tam['row_count'] = tam['price'].groupby(level=0).transform('count')
        tam['any_trades'] = (tam['row_count'] > 1) & (tam['share_trades'] > 0)
        if tam['any_trades'].any():
            tam.drop(['row_count', 'any_trades'], 1, inplace=True)
            # we now know there are buys with multiple accounts
            # now we get the account with the highest cash
            self.utility_add_cash(tam, cash)
            self.utility_get_unique_max(tam, 'cash', output_field='max_cash', index_level=1)
            # make a copy of the account with highest cash only
            account = tam[tam['max_cash']].copy()
            tam.drop(['cash', 'max_cash'], 1, inplace=True)
            account['dollar_trade'] = account['share_trades'] * account['price']
            account.drop(account[account.share_trades < 0].index, inplace=True)
            account.loc[:, 'min_trade'] = account['dollar_trade'].min()
            account.loc[:, 'is_eligible'] = (account.loc[:, 'cash'] > account.loc[:, 'min_trade']) & (
                account.share_trades > 0)
            if account['is_eligible'].any():
                account.drop(account[~account.is_eligible].index, inplace=True)
                self.utility_get_unique_max(account, 'dollar_trade', output_field='max_trade')
                account.drop(account[~account.max_trade].index, inplace=True)
                account.drop(['cash', 'max_cash', 'dollar_trade', 'min_trade', 'is_eligible', 'max_trade'], 1, inplace=True)
                tam['size'] = account['share_trades']
                return True
            else: return False
        else:
            tam.drop(['row_count', 'any_trades'], 1, inplace=True)
            return False

    def buy_multiple_complete(self, tam, cash):
        """
        Instructs trades where buy is held in multiple accounts and at least one account has enough cash to complete the entire buy. See notes 12/04/17.
        :param tam: dataframe
        :param cash: dataframe
        :return: bool
        """
        tam['row_count'] = tam['price'].groupby(level=0).transform('count')
        tam['any_trades'] = (tam['row_count'] > 1) & (tam['share_trades'] > 0)
        if tam['any_trades'].any():
            # we now know there are buys with multiple accounts
            tam['dollar_trade'] = tam['share_trades'] * tam['price']
            self.utility_add_cash(tam, cash)
            # We're not actually trying to loop through all the accounts. We loop until we find an account with a qualifying trade, execute, and return true.
            for name, account in tam.groupby(level=1):
                account = account.copy()
                account.drop(account[account.share_trades < 0].index, inplace=True)
                account.loc[:,'min_trade'] = account['dollar_trade'].min()
                account.loc[:,'is_eligible'] = (account.loc[:,'cash'] > account.loc[:,'min_trade']) & (account.share_trades > 0)
                if account['is_eligible'].any():
                    # We have an account that has enough cash for at least one trade. Other wise we return false and continue the for loop.
                    # So next we say every trade is eligible
                    account.loc[:,'eligible'] = account[account['is_eligible']]['dollar_trade']
                    # Sum the eligible trades
                    account.loc[:,'sum_trades'] = account['eligible'].sum()
                    # check if the account has enough cash to do all trades
                    account.loc[:,'sufficient'] = (account['sum_trades'] < account['cash'])
                    # We start by checking if the account has enough cash to buy every existing account holding. If it doesn't we remove largest trade and continue. See log 12/04/17.
                    while ~account['sufficient'].any():
                        account.loc[:,'is_eligible'] = ~(account['eligible'] == account['eligible'].max())
                        account.drop(account[~account.is_eligible].index, inplace=True)
                        account.loc[:,'eligible'] = account.loc[account['is_eligible']]['eligible']
                        account.loc[:,'sum_trades'] = account['eligible'].sum()
                        account.loc[:,'sufficient'] = (account['sum_trades'] < account['cash'])
                    tam.loc[:,'select'] = account['is_eligible']
                    tam['select'].fillna(False, inplace=True)
                    tam.loc[:,'size'] = tam[tam['select']]['share_trades']
                    tam.drop(['row_count', 'any_trades', 'select', 'dollar_trade', 'cash'], 1, inplace=True)
                    return True
                else:
                    tam.drop(['dollar_trade', 'cash'], 1, inplace=True)
                    return False
        else:
            tam.drop(['row_count', 'any_trades'], 1, inplace=True)
            return False

    def buy_multiple_partial(self, tam, cash):
        """
        For each symbol with an existing holding buys any possible amounts with available cash.
        :param tam:
        :param cash:
        :return:
        """
        if tam.empty: return False
        tam['row_count'] = tam['share_trades'].groupby(level=0).transform(lambda x: x.sum() > 0)
        tam['row_count'] = tam['row_count'].astype(bool)
        tam['any_trades'] = (tam['row_count']) & (tam['share_trades'] > 0)
        if tam['any_trades'].any():
            tam['dollar_trade'] = tam['share_trades'] * tam['price']
            self.utility_add_cash(tam, cash)
            tam['cash_by_symbol'] = tam['cash'].groupby(level=0).transform(lambda x: x.sum())
            tam['cash_less_dollar'] = tam['cash_by_symbol'] - tam['dollar_trade']
        else: return False
        if (tam['cash_less_dollar'] > 0).any():
            trades = pd.Series()
            self.utility_get_unique_max(tam, 'cash_less_dollar', index_level=0)
            account = tam.loc[tam.loc[:,'eligible'],:].copy()
            # select account
            while True:
                # set trade to instruct
                self.utility_get_unique_max(account, 'cash', index_level=1)
                if account[account['eligible']]['cash'][0] > account[account['eligible']]['dollar_trade'][0]:
                    trades = trades.append(account[account['eligible']]['share_trades'])
                else: trades = trades.append(round(account[account['eligible']]['cash'] / account[account['eligible']]['price'], 0))
                # update portfolio trades
                account.loc[:, 'share_change'] = trades[0]
                account.share_change.fillna(0, inplace=True)
                account.loc[:,'share_trades'] = account.share_trades - account.share_change
                account.drop('share_change', 1, inplace=True)
                account.dollar_trade = account.share_trades * account.price
                if (account.share_trades < 0).any(): break
                # cash change
                account.loc[:, 'cash_change'] = account.loc[account.loc[:, 'eligible'], 'cash']
                account.cash_change.fillna(0, inplace=True)
                account.loc[:, 'cash'] = account.cash - account.cash_change
                account.drop('cash_change', 1, inplace=True)
                # keep going?
                if (account.dollar_trade > account.cash).all(): break
            tam['size'] = trades
            tam.drop(['row_count', 'any_trades', 'dollar_trade', 'cash', 'cash_by_symbol', 'cash_less_dollar', 'eligible'], 1, inplace=True)
            return True
        else:
            return False

    def buy_multiple_partial_one_trade(self, tam, cash):
        """
        This is an alternative to buy_multiple_partial. It instructs one partial buy at a time.
        :param tam: dataframe
        :param cash: dataframe
        :return: bool
        """
        tam['row_count'] = tam['price'].groupby(level=0).transform('count')
        tam['any_trades'] =  (tam['share_trades'] > 0) & (tam['row_count'] > 1)
        if tam['any_trades'].any():
            tam.drop(['any_trades', 'row_count'], 1, inplace=True)
            # we now know there are partial buys
            # now we get the account with the highest cash
            self.utility_add_cash(tam, cash)
            self.utility_get_unique_max(tam, 'cash', output_field='max_cash', index_level=1)
            # make a copy of the account with highest cash only
            account = tam[tam['max_cash']].copy()
            if (account.cash < account.price).all():
                tam.drop(['cash', 'max_cash'], 1, inplace=True)
                return False
            tam.drop(['cash', 'max_cash'], 1, inplace=True)
            account['dollar_trade'] = account['share_trades'] * account['price']
            account.drop(account[account.share_trades < 0].index, inplace=True)
            self.utility_get_unique_max(account, 'dollar_trade', output_field='max_dollar_trade')
            account.drop(account[~account.max_dollar_trade].index, inplace=True)
            tam['size'] = (account.cash/account.price).apply(lambda x: math.trunc(x))
            return True
        else:
            tam.drop(['any_trades', 'row_count'], 1, inplace=True)
            return False

    def buy_single_partial(self, tam, cash):
        """

        :param tam:
        :param cash:
        :return:
        """
        tam['row_count'] = tam['price'].groupby(level=0).transform('count')
        tam['any_trades'] = (tam['share_trades'] > 0) & (tam['row_count'] == 1)
        if tam['any_trades'].any():

            # we now know there are partial buys where only one account holds it but has insufficient cash
            # now we get the account with the highest cash
            self.utility_add_cash(tam, cash)
            self.utility_get_unique_max(tam, 'cash', output_field='max_cash', index_level=1)
            # make a copy of the account with highest cash only
            account = tam[tam['max_cash'] & tam['any_trades']].copy()
            if account.cash.sum() == 0:
                tam.drop(['cash', 'max_cash', 'any_trades', 'row_count'], 1, inplace=True)
                return False
            tam.drop(['cash', 'max_cash', 'any_trades', 'row_count'], 1, inplace=True)
            account['dollar_trade'] = account['share_trades'] * account['price']
            account.drop(account[account.share_trades < 0].index, inplace=True)
            if account.shape[0] > 1:
                self.utility_get_unique_max(account, 'dollar_trade', output_field='max_dollar_trade')
                account.drop(account[~account.max_dollar_trade].index, inplace=True)
            tam['size'] = (account.cash / account.price).apply(lambda x: math.trunc(x))
            return True
        else:
            tam.drop(['any_trades', 'row_count'], 1, inplace=True)
            return False

    def buy_new_complete(self, tam, cash):
        """
        Buys new holdings using the account with the highest cash.
        ASSUMPTION: All other possible trades have been instructed and removed from the TAM.
        :param tam:
        :param cash:
        :return:
        """
        if (tam['share_trades'] > 0).any():
            # Get highest cash and add that account number and cash balance to tam.
            self.utility_get_unique_max(cash, 'shares', output_field='max_cash')
            account_cash = cash.groupby(cash.index)
            for key, group in account_cash:
                if group.max_cash.iloc[0]:
                    tam['account'] = account_number = key
                    tam['cash'] = group['shares'][0]
            # Check smallest trade is greater than largest balance and return false if true as no trade possible. tam and cash cleanup included.
            tam['dollar_trades'] = tam.price * tam.share_trades
            self.utility_get_unique_min(tam, 'dollar_trades', output_field='min_trade')
            new_account = tam.reset_index().copy()
            no_trade = (tam[tam.min_trade].cash < tam[tam.min_trade].dollar_trades).all()
            tam.drop(['account', 'cash', 'dollar_trades', 'min_trade'], 1, inplace=True)
            cash.drop(['max_cash'], 1, inplace=True)
            if no_trade:
                return False
            """We have eligible trades. Now we will manipulate new_account. We reset the index on new_account because were going to refashion it to have the same index as tam. 
            
            The crucial change is in the account number. Before each trade was associated with a model or account number. But since were buying a new holding we make all these trades associated with the account we've selected."""
            new_account.drop(['account_number'], 1, inplace=True)
            new_account.rename(columns= {'account': 'account_number'}, inplace=True )
            new_account.set_index(['symbol', 'account_number'], inplace=True)
            new_account['shares'] = 0
            new_account.drop_duplicates(inplace=True)
            self.utility_get_unique_max(new_account, 'dollar_trades', output_field='max_trade')
            new_account['enough_cash'] = (new_account['cash'] > new_account['dollar_trades'])
            if ~new_account.enough_cash.all():
                return False
            new_account = new_account[new_account.max_trade]
            symbol = new_account.index.get_level_values('symbol')[0]
            new_account['size'] = new_account.share_trades
            new_account.drop(['cash', 'dollar_trades', 'min_trade', 'max_trade', 'enough_cash'], 1, inplace=True)
            tam['size'] = np.nan
            for key, group in new_account.groupby(new_account.index):
                tam.loc[key,:] = group.values.tolist()[0]
            if new_account.index.get_level_values(level=0)[0] == 'model':
                tam.drop([(symbol, 'model')], inplace=True)

            return True
        else:
            return False

    def buy_new_partial(self, tam, cash):
        """
                Buys new holdings using the account with the highest cash.
                ASSUMPTION: All other possible trades have been instructed and removed from the TAM.
                :param tam:
                :param cash:
                :return:
                """
        if (tam['share_trades'] > 0).any():
            # Get highest cash and add that account number and cash balance to tam.
            self.utility_get_unique_max(cash, 'shares', output_field='max_cash')
            account_cash = cash.groupby(cash.index)
            for key, group in account_cash:
                if group.max_cash.iloc[0]:
                    tam['account'] = account_number = key
                    tam['cash'] = group['shares'][0]
            # Check smallest trade is greater than largest balance and return false if true as no trade possible. tam and cash cleanup included.
            tam['dollar_trades'] = tam.price * tam.share_trades
            if (tam.cash < tam.price).all():
                tam.drop(['account', 'cash', 'dollar_trades'], 1, inplace=True)
                return False
            # trade present, create new df and cleanup
            new_account = tam.reset_index().copy()
            tam.drop(['account', 'cash', 'dollar_trades'], 1, inplace=True)
            cash.drop(['max_cash'], 1, inplace=True)
            # update dataframe with same index as tam and complete trade selection
            new_account.drop_duplicates(inplace=True)
            new_account.drop(['account_number'], 1, inplace=True)
            new_account.rename(columns={'account': 'account_number'}, inplace=True)
            new_account.set_index(['symbol', 'account_number'], inplace=True)
            new_account['shares'] = 0
            self.utility_get_unique_max(new_account, 'dollar_trades', output_field='max_trade')
            new_account = new_account[new_account.max_trade]
            symbol = new_account.index.get_level_values(0)[0]
            new_account['size'] = (new_account.cash / new_account.price).apply(lambda x: math.trunc(x))
            new_account.drop(['cash', 'dollar_trades', 'max_trade'], 1, inplace=True)
            tam['size'] = np.nan
            for key, group in new_account.groupby(new_account.index):
                tam.loc[key, :] = group.values.tolist()[0]
            return True
        else:
            return False

    def utility_get_unique_max(self, df, input_field, output_field='eligible', index_level=0):
        dupe_counter = 0
        for name, symbol in df.groupby(level=index_level):
            symbol = symbol.copy()
            if symbol[input_field].max() == df[input_field].max():
                dupe_counter += 1
            if dupe_counter > 1:
                symbol[output_field] = True
                df.loc[:,output_field] = symbol[output_field]
                break
        else:
            df.loc[:,output_field] = df[input_field].groupby(level=index_level).transform(lambda x: x.max() == df[input_field].max()).astype(bool)
        df[output_field].fillna(False, inplace=True)

    def utility_get_unique_min(self, df, input_field, output_field='eligible', index_level=0):
        dupe_counter = 0
        for name, symbol in df.groupby(level=index_level):
            symbol = symbol.copy()
            if symbol[input_field].min() == df[input_field].min():
                dupe_counter += 1
            if dupe_counter > 1:
                symbol[output_field] = True
                df.loc[:,output_field] = symbol[output_field]
                break
        else:
            df.loc[:,output_field] = df[input_field].groupby(level=index_level).transform(lambda x: x.min() == df[input_field].min()).astype(bool)
        df[output_field].fillna(False, inplace=True)

    def utility_add_cash(self, tam, cash):
        tam.reset_index(level=0, inplace=True)
        tam['cash'] = cash
        tam.cash.fillna(0, inplace=True)
        tam.reset_index(inplace=True)
        tam.set_index(['symbol', 'account_number'], inplace=True)


class TradeInstructions(object):
    def __init__(self):
        self._trades = pd.DataFrame()

    @property
    def trades(self):
        return self._trades

    @trades.setter
    def trades(self, tam):
        self._trades = pd.concat([self._trades, tam.loc[~tam['size'].isnull()]])

    def clean_up_trades(self):
        self._trades.drop(['shares'], inplace=True)

    def prepare_for_transmission(self):
        if self.trades.empty:
            self.instructions = pd.DataFrame(['no_trades'])
        else:
            self.instructions = self.trades.copy().reset_index().loc[:,['symbol', 'account_number', 'size']]

class TradeAlgorithms(object):
    def __init__(self):
        pass

    def sell_position(self, target: float, current: float) -> float:
        return target - current


