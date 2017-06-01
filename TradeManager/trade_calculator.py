import pandas as pd
from TradeManager.test.test_data.test_data import prices

class TradeCalculator(object):
    def __init__(self, portfolio, model, prices):
        self.model = model
        self.portfolio = portfolio
        self.prices = prices
        self.portfolio_trade_list = self._add_share_trades()
        # self.buy_trades = self._split_trade_list()

    def _get_dollar_trades(self, portfolio, model):
        portfolio_model_weights = pd.concat([model, self.portfolio.portfolio_positions['portfolio_weight']], axis=1).fillna(0)
        portfolio_model_weights['price'] = self.prices.prices
        portfolio_model_weights['dollar_trades'] = (portfolio_model_weights['model_weight'] - portfolio_model_weights['portfolio_weight']) * self.portfolio.portfolio_value
        return portfolio_model_weights

    def _add_share_trades(self):
        trade_list = self._get_dollar_trades(self.portfolio, self.model)
        trade_list['shares'] = (trade_list['dollar_trades']/trade_list['price']).round()

        return trade_list

    def _split_trade_list(self, type='Buy'):
        if type == 'Buy':
            return self.portfolio_trade_list[self.portfolio_trade_list['shares'] < 0]
        else:
            return self.portfolio_trade_list[self.portfolio_trade_list['shares'] > 0]

    def request_prices(self):
        """Need to update this to fetch portfolio and model prices only."""
        return pd.DataFrame(prices).set_index('symbol')

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])