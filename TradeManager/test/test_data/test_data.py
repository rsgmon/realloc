import pandas as pd

# test_data structure is how tradeshop expects it
trade_request = {'portfolio_id': 'a1', 'account_numbers': ['11-11', 'X4-557'], 'model_id': 'TTT'}

accounts = [{'account_number': '11-11', 'account_positions': [{'symbol': 'MMM', 'shares': 500, 'price': 40}, {'symbol': 'XYZ', 'shares': 100, 'price': 43. }, {'symbol':'cash', 'shares': 25000, 'price': 1}] }, {'account_number': 'X4-557', 'account_positions': [{'symbol': 'XYZ', 'shares': 100, 'price': 43}, {'symbol': 'DEF', 'shares': 100, 'price': 212}, {'symbol':'cash', 'shares': 5000, 'price': 1}]}]

model = {'model_id': 'TTT', 'model_positions': [{'symbol': 'ABC', 'weight': 0.15}, {'symbol': 'DEF', 'weight': 0.05}, {'symbol': 'GGG', 'weight': 0.05}, {'symbol': 'cash', 'weight': 0.05}]}

prices = [{'symbol': 'MMM', 'price': 40}, {'symbol': 'XYZ', 'price': 43},
          {'symbol': 'DEF', 'price': 212}, {'symbol': 'ABC', 'price': 120},
          {'symbol': 'GGG', 'price': 34}, {'symbol': 'cash', 'price': 1}]



account_instructions = 'C:\\Users\\Rye\\Google Drive\\School\\Python\\PortMgr\\TradeManager\\test\\test_data\\account_data.json'