# test_data structure is how tradeshop expects it
import pandas as pd

raw_accounts = [
    {'account_number': '11-12', 'account_positions': [{'symbol': 'MMM', 'shares': 500, 'price': 40},
                                                      {'symbol': 'DEF', 'shares': 100, 'price': 43.},
                                                      {'symbol': 'cash', 'shares': 25000, 'price': 1}]},
    {'account_number': 'X4-557', 'account_positions': [{'symbol': 'YOU', 'shares': 100, 'price': 43},
                                                       {'symbol': 'MMM', 'shares': 100, 'price': 212},
                                                       {'symbol': 'cash', 'shares': 5000, 'price': 1}]}]

raw_model = {'model_id': 'TTT',
             'model_positions': [
                 {'symbol': 'ABC', 'model_weight': 0.15}, {'symbol': 'DEF', 'model_weight': 0.05},
                 {'symbol': 'GGG', 'model_weight': 0.05}, {'symbol': 'cash', 'model_weight': 0.05}]}

model_instructions = {'instructions': 'instructions'}
model_request_raw_model = {'raw_model': raw_model}
model_request_instructions = {'instructions': model_instructions}
model_request_both = {'instructions': model_instructions, 'raw_model': raw_model}

prices = [{'symbol': 'MMM', 'price': 40}, {'symbol': 'XYZ', 'price': 43},
          {'symbol': 'DEF', 'price': 212}, {'symbol': 'ABC', 'price': 120},
          {'symbol': 'GGG', 'price': 34}, {'symbol': 'cash', 'price': 1}
    , {'symbol': 'GHI', 'price': 43}, {'symbol': 'YOU', 'price': 43}]

account_instructions = [
    'C:\\Users\\Rye\\Google Drive\\School\\Python\\PortMgr\\TradeManager\\test\\test_data\\abc_broker.json',
    'C:\\Users\\Rye\\Google Drive\\School\\Python\\PortMgr\\TradeManager\\test\\test_data\\xyz_broker.json']

# trade_requests
blank = {}
no_port_raw_model = {'portfolio_id': 'a1', 'model_request': model_request_raw_model}
acc_inst_no_model = {'portfolio_id': 'a1', 'account_instructions': account_instructions}
acc_inst_both_models = {'portfolio_id': 'a1', 'portfolio_request': {'account_instructions': account_instructions,
                                                                    'raw_acounts': raw_accounts}}
acc_inst_raw_model = {'portfolio_id': 'a1', 'account_instructions': account_instructions,
                      'model_request': model_request_raw_model}
acc_inst_two_models = {'portfolio_id': 'a1', 'account_instructions': account_instructions,
                       'model_request': model_request_both}
#This should be reinserted into valid request for testing'account_instructions': account_instructions,
valid_request = {'portfolio_id': 'a1',
                 'portfolio_request': {'raw_accounts': raw_accounts},
                 'model_request': model_request_raw_model}

