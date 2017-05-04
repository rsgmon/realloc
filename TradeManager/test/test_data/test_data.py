# test_data structure is how tradeshop expects it
import pandas as pd

prices = [{'symbol': 'ABC', 'price': 120}, {'symbol': 'DEF', 'price': 212}, {'symbol': 'GGG', 'price': 34},
          {'symbol': 'GHI', 'price': 43}, {'symbol': 'MMM', 'price': 40}, {'symbol': 'YOU', 'price': 43},
          {'symbol': 'XYZ', 'price': 43}, {'symbol': 'cash', 'price': 1}]

one_holding = {'account_number': '22-22', 'account_positions': [{'symbol': 'MMM', 'shares': 500, 'price': 40},
                                                                {'symbol': 'cash', 'shares': 25000, 'price': 1}]}
two_holding = {'account_number': 'X4-557', 'account_positions': [{'symbol': 'YOU', 'shares': 100, 'price': 43},
                                                                 {'symbol': 'MMM', 'shares': 100, 'price': 212},
                                                                 {'symbol': 'cash', 'shares': 25000, 'price': 1}]}
three_holding = {'account_number': '11-12', 'account_positions': [{'symbol': 'DEF', 'shares': 100, 'price': 43.},
                                                                  {'symbol': 'MMM', 'shares': 500, 'price': 40},
                                                                  {'symbol': 'YOU', 'shares': 100, 'price': 43},
                                                                  {'symbol': 'cash', 'shares': 25000, 'price': 1}]}
raw_account_1 = [one_holding]
raw_account_1_2 = [one_holding, two_holding]
raw_account_2_3 = [two_holding, three_holding]

zero_model = {'model_id': 'TTT', 'model_positions': []}
one_position = {'model_id': 'TTT', 'model_positions': [{'symbol': 'DEF', 'model_weight': 1}]}
equal_weighted_model = {'model_id': 'TTT', 'model_positions': [
    {'symbol': 'MMM', 'model_weight': 0.25}, {'symbol': 'DEF', 'model_weight': 0.25},
    {'symbol': 'YOU', 'model_weight': 0.25}]}

trade_requests = {}
trade_requests['one_holding_zero_model'] = {'portfolio_id': 'a1', 'portfolio_request': {'raw_accounts': raw_account_1},
                          'model_request': {'raw_model': zero_model}}
trade_requests['one_holding_one_position'] = {'portfolio_id': 'a1', 'portfolio_request': {'raw_accounts': raw_account_1},
                            'model_request': {'raw_model': one_position}}
trade_requests['one_holding_equal_weighted'] = {'portfolio_id': 'a1', 'portfolio_request': {'raw_accounts': raw_account_1},
                              'model_request': {'raw_model': equal_weighted_model}}
trade_requests['one_holding_two_holding_zero_model'] = {'portfolio_id': 'a1', 'portfolio_request': {'raw_accounts': raw_account_1_2},
                              'model_request': {'raw_model': zero_model}}
trade_requests_keys = trade_requests.keys()


# ----These mocks test TradeRequest validation works. Some are only imported into test_model or used later.----
account_instructions = [
    'C:\\Users\\Rye\\Google Drive\\School\\Python\\PortMgr\\TradeManager\\test\\test_data\\abc_broker.json',
    'C:\\Users\\Rye\\Google Drive\\School\\Python\\PortMgr\\TradeManager\\test\\test_data\\xyz_broker.json']

raw_accounts = [
    {'account_number': '11-12', 'account_positions': [{'symbol': 'MMM', 'shares': 500, 'price': 40},
                                                      {'symbol': 'DEF', 'shares': 100, 'price': 43.},
                                                      {'symbol': 'cash', 'shares': 25000, 'price': 1}]},
    {'account_number': 'X4-557', 'account_positions': [{'symbol': 'YOU', 'shares': 100, 'price': 43},
                                                       {'symbol': 'MMM', 'shares': 100, 'price': 212},
                                                       {'symbol': 'cash', 'shares': 5000, 'price': 1}]}]
raw_model = {'model_id': 'TTT',
             'model_positions': [
                 {'symbol': 'MMM', 'model_weight': 0.01}, {'symbol': 'DEF', 'model_weight': 0.05},
                 {'symbol': 'YOU', 'model_weight': 0.05}, {'symbol': 'cash', 'model_weight': 0.05}]}
blank = {}
model_instructions = {'instructions': 'instructions'}
model_request_raw_model = {'raw_model': raw_model}
model_request_instructions = {'instructions': model_instructions}
model_request_both = {'instructions': model_instructions, 'raw_model': raw_model}
no_port_raw_model = {'portfolio_id': 'a1', 'model_request': model_request_raw_model}
acc_inst_no_model = {'portfolio_id': 'a1', 'account_instructions': account_instructions}
acc_inst_both_models = {'portfolio_id': 'a1', 'portfolio_request': {'account_instructions': account_instructions,
                                                                    'raw_acounts': raw_accounts}}
acc_inst_raw_model = {'portfolio_id': 'a1', 'account_instructions': account_instructions,
                      'model_request': model_request_raw_model}
acc_inst_two_models = {'portfolio_id': 'a1', 'account_instructions': account_instructions,
                       'model_request': model_request_both}


#This should be reinserted into valid request for testing'account_instructions': account_instructions,

