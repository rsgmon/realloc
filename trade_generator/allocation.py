import pandas as pd
import numpy as np

class AllocationController:
    def __init__(self, portfolio, trade_calculator):
        self.portfolio = portfolio
        self.trade_calculator = trade_calculator
        self.trade_instructions = TradeInstructions()

    def allocate_trades(self):
        if len(self.portfolio.account_numbers) == 1:
            self.trade_selector = SingleAccountTradeSelector(self.portfolio, self.trade_calculator.portfolio_trade_list)
        else:
            self.trade_selector = MultipleAccountTradeSelector(self.portfolio, self.trade_calculator.portfolio_trade_list)

        self.trade_selector.get_trades()
        return self.trade_selector.trade_instructions


class TradeSelector:
    def __init__(self, portfolio, portfolio_trade_list):
        self.trade_account_matrix = TradeAccountMatrix(portfolio, portfolio_trade_list)
        self.trade_instructions = TradeInstructions()
        self.trading_library = TradingLibrary()

    def has_buys(self):
        return (self.trade_account_matrix.portfolio_trade_list['share_trades'] > 0).any()

    def has_sells(self):
        return (self.trade_account_matrix.portfolio_trade_list['share_trades'] < 0).any()


class SingleAccountTradeSelector(TradeSelector):
    def get_trades(self):
        tam = self.trade_account_matrix.trade_account_matrix
        if self.has_sells():
            sell_trades = self.trading_library.single_account_sell(tam)
            sell_trades['size'] = sell_trades.share_trades
            self.trade_instructions.add_trades(sell_trades)

        if self.has_buys():
            buy_trades = self.trading_library.single_account_buy(tam)
            buy_trades['size'] = buy_trades.share_trades
            self.trade_instructions.add_trades(buy_trades)


class MultipleAccountTradeSelector(TradeSelector):
    def get_trades(self):
        tam = self.trade_account_matrix.trade_account_matrix
        if self.has_sells():
            self._process_sell_trades()
        if self.has_buys():
            self._process_buy_trades()

    def _process_sell_trades(self):
        tam = self.trade_account_matrix.trade_account_matrix
        while (tam['share_trades'] < 0).any():
            self.trading_library.sell_best_option(tam)
            self.trade_account_matrix.update_tam()
            self.trade_instructions.add_trades(tam)

    def _process_buy_trades(self):
        tam = self.trade_account_matrix.trade_account_matrix
        while (tam['share_trades'] > 0).any():
            self.trading_library.buy_best_option(tam)
            self.trade_account_matrix.update_tam()
            self.trade_instructions.add_trades(tam)


class TradeInstructions:
    def __init__(self):
        self._trades = pd.DataFrame()

    @property
    def trades(self):
        return self._trades

    def add_trades(self, tam):
        if not tam.empty:
            self._trades = pd.concat([self._trades, tam.loc[~tam['size'].isnull()]]).drop_duplicates()

    def clean_up_trades(self):
        self._trades.drop(['shares'], inplace=True, errors='ignore')

    def prepare_for_transmission(self):
        if self.trades.empty:
            self.instructions = pd.DataFrame(['no_trades'])
        else:
            self.instructions = self.trades.copy().reset_index().loc[:,['symbol', 'account_number', 'size']]
