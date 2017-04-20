import pandas as pd
import numpy as np
from TradeManager.portfolio import Portfolio

# these are intermediate test data structures
account_numbers = {'account_numbers': ['11-11', 'X4-557']}
model_positions = pd.DataFrame([{'symbol': 'ABC', 'weight': 0.15}, {'symbol': 'DEF', 'weight': 0.05}, {'symbol': 'GGG', 'weight': 0.05}, {'symbol': 'cash', 'weight': 0.05}]).rename(
    columns={'weight':'model_weight'}).groupby('symbol').agg(np.sum)
portfolio = Portfolio(account_numbers)
prices = pd.DataFrame([{'symbol': 'MMM', 'price': 40}, {'symbol': 'XYZ', 'price': 43},
          {'symbol': 'DEF', 'price': 212}, {'symbol': 'ABC', 'price': 120},
          {'symbol': 'GGG', 'price': 34}, {'symbol': 'cash', 'price': 1}]).set_index('symbol')
trade_list = pd.DataFrame({'trades' : pd.Series([11970, -17210, 3990, -20000, -86000, -26010]
                                                , index=['ABC', 'DEF', 'GGG', 'MMM', 'XYZ', 'cash'])})
