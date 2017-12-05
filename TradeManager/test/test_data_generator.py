# import TradeManager.allocation as allocate
import TradeManager.portfolio as portfolio
import TradeManager.trade_calculator as tc
import TradeManager.trade_manager as trade_manage
import TradeManager.allocation as al
import pickle
import argparse
import sys
import os

# Single responibility principle. YOUR RUSHING!!
# pickle_trade_request and pickle_prices do more than one thing
# parse the folders and paths in another function


def pickle_trade_request(source, destination):
    request = trade_manage.TradeRequest(trade_manage.RawRequest('xl', source))
    # with open(destination + 'request.pkl', 'wb') as myfile:
    #     pickle.dump(request, myfile)
    return request

def pickle_prices(source, destination, test_prices=True, **myargs):
    prices = trade_manage.PriceRetriever(trade_manage.RawRequest('xl', source))
    if test_prices:
        prices()
    else:
        print(myargs['file'], myargs['test_array_index'])
    # with open(destination + '\/prices.pkl', 'wb') as myprices:
    #     pickle.dump(prices, myprices)
    return prices

def pickle_portfolios_models(trade_request, prices, destination):
    port = portfolio.Portfolio(trade_request.portfolio_request, prices)
    # with open(destination + '\/portfolio.pkl', 'wb') as myfile:
    #     pickle.dump(port, myfile)
    model = trade_manage.Model(trade_request.model_request)
    # with open(destination + '\/model.pkl', 'wb') as modelfile:
    #     pickle.dump(model, modelfile)
    return port, model

def pickle_trade_calculator(portfolio, model, prices, destination):
    trade_calculator = tc.TradeCalculator(portfolio, model, prices)
    # with open(destination + 'trade_list.pkl', 'wb') as myfile:
    #     pickle.dump(trade_calculator, myfile)
    return trade_calculator

def pickle_allocation(portfolio, trade_calculator):
    allocation_controller = al.AllocationController(portfolio, trade_calculator)
    allocated_trades = allocation_controller.allocate_trades()
    # with open(destination + 'allocation.pkl', 'wb') as myfile:
    #     pickle.dump(allocated_trades, myfile)
    return allocated_trades

def pickle_tam(portfolio, trade_calculator):
    tam = al.TradeAccountMatrix(portfolio, trade_calculator.portfolio_trade_list)
    with open(destination + file_output_name + '_tam.pkl', 'wb') as myfile:
        pickle.dump(tam, myfile)

def read_pickle(file):
    with open(file, 'rb') as afile:
        apickle = pickle.load(afile)
    return apickle

def _parse_args(args=None):
    # if not args: return None
    parser = argparse.ArgumentParser(description='Path to the config file.')
    parser.add_argument('source_path', help='Path relative to ./test\/test_data.')
    parser.add_argument('source_name', help='Name of test data file.')
    parser.add_argument('destination_path', help='Example sellsOnly or sellsOnly\/singleSell')
    parser.add_argument('command', help='Name of the function to apply. Each function generates different pickles.')
    parser.add_argument('--file_name', help='Name of the test output file')

    return parser.parse_args(args)

def _build_paths(source_path, source_file, destination_path):
    source = source_path + '\/' + source_file
    destination = destination_path + '\/'
    return source, destination

def generate_with_one_pickle():
    request = pickle_trade_request(source, destination)
    prices = pickle_prices(source, destination)
    portfolio, model = pickle_portfolios_models(request, prices.prices, destination)
    trade_calculator = pickle_trade_calculator(portfolio, model, prices.prices, destination)
    pickle_tam(portfolio, trade_calculator)

def generate_with_all_pickles():
    request = pickle_trade_request(source, destination)
    with open(destination + 'request.pkl', 'wb') as myfile:
        pickle.dump(request, myfile)
    prices = pickle_prices(source, destination)
    with open(destination + 'prices.pkl', 'wb') as myprices:
        pickle.dump(prices, myprices)
    portfolio, model = pickle_portfolios_models(request, prices.prices, destination)
    with open(destination + 'portfolio.pkl', 'wb') as myfile:
        pickle.dump(portfolio, myfile)
    with open(destination + 'model.pkl', 'wb') as modelfile:
        pickle.dump(model, modelfile)
    trade_calculator = pickle_trade_calculator(portfolio, model, prices.prices, destination)
    with open(destination + 'trade_calculator.pkl', 'wb') as myfile:
        pickle.dump(trade_calculator, myfile)
    pickle_tam(portfolio, trade_calculator)

def generate_portfolios_and_portfolio_trade_lists():
    request = pickle_trade_request(source, destination)
    prices = pickle_prices(source, destination)
    portfolio, model = pickle_portfolios_models(request, prices.prices, destination)
    with open(destination + file_output_name + '_portfolio.pkl', 'wb') as myfile:
        pickle.dump(portfolio, myfile)
    trade_calculator = pickle_trade_calculator(portfolio, model, prices.prices, destination)
    with open(destination + file_output_name + '_trade_calculator.pkl', 'wb') as myfile:
        pickle.dump(trade_calculator, myfile)

def generate_portfolio_model_prices():
    request = pickle_trade_request(source, destination)
    prices = pickle_prices(source, destination)
    with open(destination + file_output_name + '_prices.pkl', 'wb') as myprices:
        pickle.dump(prices, myprices)
    portfolio, model = pickle_portfolios_models(request, prices.prices, destination)
    with open(destination + file_output_name + '_portfolio.pkl', 'wb') as myfile:
        pickle.dump(portfolio, myfile)
    with open(destination + file_output_name + '_model.pkl', 'wb') as modelfile:
        pickle.dump(model, modelfile)

def generate_trade_request_prices():
    request = pickle_trade_request(source, destination)
    with open(destination + file_output_name + '_request.pkl', 'wb') as myfile:
        pickle.dump(request, myfile)
    prices = pickle_prices(source, destination)
    with open(destination + file_output_name + '_prices.pkl', 'wb') as myprices:
        pickle.dump(prices, myprices)


if __name__ == "__main__":
    FUNCTION_MAP = {'generate_trade_request_prices':generate_trade_request_prices,'generate_with_one_pickle': generate_with_one_pickle,'generate_portfolios_and_portfolio_trade_lists': generate_portfolios_and_portfolio_trade_lists, 'generate_with_all_pickles': generate_with_all_pickles, 'generate_portfolio_model_prices': generate_portfolio_model_prices}
    args = _parse_args(sys.argv[1:])
    path = os.getcwd() + '\/TradeManager\/test\/test_data\/'
    source_path_only = path + args.source_path
    source, destination = _build_paths(args.source_path, args.source_name, args.destination_path)
    source = path + source
    destination = path + destination
    file_output_name = args.file_name
    func = FUNCTION_MAP[args.command]
    func()
