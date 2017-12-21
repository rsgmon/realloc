# ================== Generate Tams
# === Buy Only
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_single_target_actual.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_single_target_actual
# python .\TradeManager\test\test_data_generator.py sheets\buy_only  multi_account_single_target_actual_02.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_single_target_actual_02
# python .\TradeManager\test\test_data_generator.py sheets\buy_only  multi_account_target_actual.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_target_actual
# python .\TradeManager\test\test_data_generator.py sheets\buy_only  multi_account_target_actual_02.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_target_actual_02
# python .\TradeManager\test\test_data_generator.py sheets\buy_only  multi_account_target_single_actual.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_target_single_actual
# python .\TradeManager\test\test_data_generator.py tams\buy_only\sheets  single_account_actual_multi_target.xlsx tams\buy_only generate_with_one_pickle --file_name single_account_actual_multi_target
# python .\TradeManager\test\test_data_generator.py tams\buy_only\sheets  single_account_actual_target.xlsx tams\buy_only generate_with_one_pickle --file_name single_account_actual_target
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_target_new_holding_only.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_target_new_holding_only
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_target_new_holding_only_sufficient_cash_in_one_account_for_all_new_trades.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_target_new_holding_only_sufficient_cash_in_one_account_for_all_new_trades
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_target_new_holding_only_sufficient_cash_one_complete_one_partial.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_target_new_holding_only_sufficient_cash_one_complete_one_partial
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_single_target_new_only_insufficient_cash.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_single_target_new_only_insufficient_cash
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_target_new_holding_only_insufficient_cash.xlsx tams\buy_only generate_with_one_pickle --file_name multi_account_target_new_holding_only_insufficient_cash



# ===  sell_only
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  multi_account_actual_equal_no_model.xlsx tams\sell_only generate_with_one_pickle --file_name multi_account_actual_equal_no_model
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  multi_account_actual_no_model.xlsx tams\sell_only generate_with_one_pickle --file_name multi_account_actual_no_model
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  multi_account_actual_single_target.xlsx tams\sell_only generate_with_one_pickle --file_name multi_account_actual_single_target
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  multi_account_target_actual_equal.xlsx tams\sell_only generate_with_one_pickle --file_name multi_account_target_actual_equal
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  single_account_model_multi_actual.xlsx tams\sell_only generate_with_one_pickle --file_name single_account_model_multi_actual
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  single_account_multi_actual_model.xlsx tams\sell_only generate_with_one_pickle --file_name single_account_multi_actual_model
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  single_account_multi_actual_no_model.xlsx tams\sell_only generate_with_one_pickle --file_name single_account_multi_actual_no_model
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  multi_account_actual_single_target_all.xlsx tams\sell_only generate_with_one_pickle --file_name multi_account_actual_single_target_all
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  multi_account_actual_target.xlsx tams\sell_only generate_with_one_pickle --file_name multi_account_actual_target
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  sell_smallest_multiple_0.xlsx tams\sell_only generate_with_one_pickle --file_name sell_smallest_multiple_0
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  sell_smallest_multiple_1.xlsx tams\sell_only generate_with_one_pickle --file_name sell_smallest_multiple_1
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  sell_smallest_multiple_2.xlsx tams\sell_only generate_with_one_pickle --file_name sell_smallest_multiple_2
# python .\TradeManager\test\test_data_generator.py sheets\sell_only  cover_all_sell_methods.xlsx tams\sell_only generate_with_one_pickle --file_name cover_all_sell_methods
python .\TradeManager\test\test_data_generator.py sheets\sell_only  cover_all_sell_methods_expanded.xlsx tams\sell_only generate_with_one_pickle --file_name cover_all_sell_methods_expanded


# ====== sell_buy
# python .\TradeManager\test\test_data_generator.py sheets\sell_buy  sell_smallest_multiple_3.xlsx tams\sell_buy generate_with_one_pickle --file_name sell_smallest_multiple_3



# ============= Generate trade requests, portfolios, models, prices, calculators from sheet
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_single_target_actual.xlsx portfolios_port_trade_lists\buy_only generate_portfolios_and_portfolio_trade_lists --file_name multi_account_single_target_actual

# python .\TradeManager\test\test_data_generator.py sheets\sell_only  multi_account_actual_equal_no_model.xlsx portfolios_port_trade_lists\sell_only generate_portfolios_and_portfolio_trade_lists --file_name multi_account_actual_equal_no_model

# ================ Generate trade_calculator from portfolios models prices
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_single_target_actual.xlsx portfolio_model_prices generate_portfolio_model_prices --file_name multi_account_single_target_actual

# python .\TradeManager\test\test_data_generator.py sheets\sell_only multi_account_actual_single_target.xlsx portfolio_model_prices generate_portfolio_model_prices --file_name sell_only_multi_account_actual_single_target
# python .\TradeManager\test\test_data_generator.py sheets\sell_only multi_account_target_actual_equal.xlsx portfolio_model_prices generate_portfolio_model_prices --file_name sell_only_multi_account_target_actual_equal

# ================= Generate portfolio from trade_request prices
# python .\TradeManager\test\test_data_generator.py sheets\buy_only multi_account_single_target_actual.xlsx trade_request_prices generate_trade_request_prices --file_name buy_only_multi_account_single_target_actual

# python .\TradeManager\test\test_data_generator.py sheets\sell_only single_account_model_multi_actual.xlsx trade_request_prices generate_trade_request_prices --file_name single_account_model_multi_target