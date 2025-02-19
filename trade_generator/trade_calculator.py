import pandas as pd

class TradeCalculator:
    def __init__(self, portfolio, model, prices):
        """
        :param portfolio: portfolio object
        :param model: model_request attribute of trade_request object
        :param prices: prices attribute of prices object
        """
        self.model = model
        self.portfolio = portfolio
        self.prices = prices
        self.portfolio_trade_list = self._calculate_trades()

    def _calculate_trades(self):
        trade_list = self._get_dollar_trades()
        if trade_list is None:
            return None

        trade_list['share_trades'] = trade_list.apply(self._calculate_share_trade, axis=1)
        trade_list.drop(columns=['shares'], inplace=True, errors='ignore')
        return trade_list

    def _calculate_share_trade(self, row):
        """
        Determines the number of shares to trade based on model weight.
        """
        if row.model_weight == 0:
            return row.shares if row.shares < 0 else -row.shares
        return round(row.dollar_trades / row.price)

    def _get_dollar_trades(self):
        """
        Computes dollar value trades by comparing portfolio allocation to model allocation.
        """
        if self.model.model_positions.empty:
            return None

        portfolio_model_weights = (
            pd.concat(
                [
                    self.model.model_positions,
                    self.portfolio.portfolio_positions[['portfolio_weight', 'shares']],
                ],
                axis=1
            ).fillna(0)
        )

        portfolio_model_weights['price'] = self.prices
        portfolio_model_weights['dollar_trades'] = (
                (portfolio_model_weights['model_weight'] - portfolio_model_weights['portfolio_weight'])
                * self.portfolio.portfolio_value
        ).round(2)

        return portfolio_model_weights

    def __str__(self):
        return '\n\n'.join(
            [f'{key}\n{value}' for key, value in self.__dict__.items()]
        )
