import pandas as pd
from TradeManager.test.test_data.test_data import prices

class TradeCalculator(object):
    def __init__(self, portfolio, model):
        self.model = model
        self.portfolio = portfolio
        self.portfolio_trade_list = self._add_share_trades()
        # self.buy_trades = self._split_trade_list()

    def _get_dollar_trades(self, portfolio, model):
        # print(pd.DataFrame(model.model_positions))
        # print(self.portfolio.portfolio['portfolio_weight'])
        portfolio_model_weights = pd.concat([model.model_positions, self.portfolio.portfolio['portfolio_weight']], axis=1).fillna(0)
        portfolio_trade_list = (portfolio_model_weights['model_weight'] - portfolio_model_weights['portfolio_weight']) * self.portfolio.portfolio_value
        portfolio_trade_list.name = 'dollar_trades'
        return pd.DataFrame(portfolio_trade_list)

    def _add_share_trades(self):
        trade_list = self._get_dollar_trades(self.portfolio, self.model)
        combined_trade_list_portfolio_prices = pd.concat([trade_list, self.request_prices()], axis=1)
        combined_trade_list_portfolio_prices['shares'] = (combined_trade_list_portfolio_prices['dollar_trades']/combined_trade_list_portfolio_prices['price']).round()
        return combined_trade_list_portfolio_prices

    def _split_trade_list(self, type='Buy'):
        if type == 'Buy':
            return self.portfolio_trade_list[self.portfolio_trade_list['shares'] < 0]
        else:
            return self.portfolio_trade_list[self.portfolio_trade_list['shares'] > 0]

    def request_prices(self):
        return pd.DataFrame(prices).set_index('symbol')