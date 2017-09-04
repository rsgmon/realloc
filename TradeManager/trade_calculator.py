import pandas as pd

class TradeCalculator(object):
    def __init__(self, portfolio, model, prices):
        """
        :param portfolio: portfolio object
        :param model: model_request attribute of trade_request object
        :param prices: prices attribute of prices object
        """
        self.model = model
        self.portfolio = portfolio
        self.prices = prices
        self.portfolio_trade_list = self._add_share_trades()


    def _get_dollar_trades(self, portfolio, model_positions):
        portfolio_model_weights = pd.concat([model_positions, portfolio.portfolio_positions['portfolio_weight'], portfolio.portfolio_positions['shares']], axis=1).fillna(0)
        portfolio_model_weights['price'] = self.prices
        portfolio_model_weights['dollar_trades'] = ((portfolio_model_weights['model_weight'] - portfolio_model_weights['portfolio_weight']) * self.portfolio.portfolio_value).round(2)
        portfolio_model_weights.index.name = 'symbol'
        return portfolio_model_weights

    def _add_share_trades(self):
        def share_trade(row):
            if row.model_weight == 0:
                return row.shares if row.shares <0 else row.shares * -1
            else:
                return (row.dollar_trades/row.price).round()
        trade_list = self._get_dollar_trades(self.portfolio, self.model.model_positions)
        trade_list['share_trades'] = trade_list.apply(share_trade, axis=1)
        trade_list.drop(['shares'], axis=1, inplace=True)
        return trade_list

    def __str__(self):
            return '\n\n'.join(['{key}\n{value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])