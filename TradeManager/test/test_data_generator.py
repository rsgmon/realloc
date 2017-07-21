# import TradeManager.allocation as allocate
import TradeManager.portfolio as portfolio
import TradeManager.trade_calculator as tc
import TradeManager.trade_manager as trade_manage
import pickle
import argparse
import sys
import os

# Single responibility principle. YOUR RUSHING!!
# pickle_trade_request and pickle_prices do more than one thing
# parse the folders and paths in another function

def pickle_trade_request(source, destination):
    request = trade_manage.TradeRequest(trade_manage.RawRequest('xl', source))
    with open(destination + 'request.pkl', 'wb') as myfile:
        pickle.dump(request, myfile)
    return request

def pickle_prices(source, destination, test_prices=True, **myargs):
    prices = trade_manage.PriceRetriever(trade_manage.RawRequest('xl', source))
    if test_prices:
        prices()
    else:
        print(myargs['file'], myargs['test_array_index'])
    with open(destination + '\/prices.pkl', 'wb') as myprices:
        pickle.dump(prices, myprices)
    return prices

def pickle_portfolios_models(trade_request, prices, destination):
    port = portfolio.Portfolio(trade_request, prices)
    with open(destination + '\/portfolio.pkl', 'wb') as myfile:
        pickle.dump(port, myfile)
    return port

def pickle_trade_calculator(portfolio, model_request, prices, destination):
    trade_calculator = tc.TradeCalculator(portfolio, model_request, prices)
    with open(destination + 'trade_list.pkl', 'wb') as myfile:
        pickle.dump(trade_calculator, myfile)
    return trade_calculator

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
    return parser.parse_args(args)

def _build_paths(source_path, source_file, destination_path):
    source = source_path + '\/' + source_file
    destination = destination_path + '\/'
    return source, destination

if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    path = os.getcwd() + '\/TradeManager\/test\/test_data\/'
    source_path_only = path + args.source_path
    source, destination = _build_paths(args.source_path, args.source_name, args.destination_path)
    source = path + source
    destination = path + destination
    request = pickle_trade_request(source, destination)
    prices = pickle_prices(source, destination)
    portfolio = pickle_portfolios_models(request.portfolio_request, prices.prices, destination)
    pickle_trade_calculator(portfolio, request.model_request, prices.prices, destination)
    # print(os.getcwd())
    # a = read_pickle('prices.pkl')
    # print(a)
    # print(a)
    # for acc in a.accounts:
    #     print(acc)
# for b in a:
#     print(b)