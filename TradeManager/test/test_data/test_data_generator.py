# import TradeManager.allocation as allocate
import TradeManager.portfolio as portfolio
import TradeManager.trade_calculator as tc
import TradeManager.trade_manager as trade_manage
import pickle
import argparse
import sys
import os

def pickle_trade_request(source_parent_folder, destination_parent_folder):
    source = source_parent_folder + '\/TradeRequest.xlsx'
    destination = destination_parent_folder + '\/request.pkl'
    mocks = trade_manage.TradeRequest(trade_manage.RawRequest('xl', source))
    with open(destination, 'wb') as myfile:
        pickle.dump(mocks, myfile)
    return mocks

def pickle_prices(source_parent_folder, destination_parent_folder, test_prices=True, **myargs):
    source = source_parent_folder + '\/TradeRequest.xlsx'
    destination = destination_parent_folder + '\/prices.pkl'
    prices = trade_manage.PriceRetriever(trade_manage.RawRequest('xl', source))
    if test_prices:
        prices()
    else:
        print(myargs['file'], myargs['test_array_index'])
    with open(destination, 'wb') as myprices:
        pickle.dump(prices, myprices)
    return prices

def pickle_portfolios_models(source_parent_folder):
    treq = read_pickle(source_parent_folder + '\/request.pkl')
    prices = read_pickle(source_parent_folder + '\/prices.pkl')
    port = portfolio.Portfolio(treq.portfolio_request, prices.prices)
    with open(source_parent_folder + '\/portfolio.pkl', 'wb') as myfile:
        pickle.dump(port, myfile)

def pickle_trade_calculator(source_parent_folder):
    portfolio = read_pickle(source_parent_folder + '\/portfolio.pkl')
    trade_request = read_pickle(source_parent_folder + '\/request.pkl')
    prices = read_pickle(source_parent_folder + '\/prices.pkl')
    model = trade_request.model_request
    trade_calculator = tc.TradeCalculator(portfolio, model, prices)
    with open(source_parent_folder + '\/trade_list.pkl', 'wb') as myfile:
        pickle.dump(trade_calculator, myfile)

def read_pickle(file):
    with open(file, 'rb') as afile:
        apickle = pickle.load(afile)
    return apickle

def _parse_args(args=None):
    # if not args: return None
    parser = argparse.ArgumentParser(description='Path to the config file.')
    parser.add_argument('source_parent_folder', help='Specify the name of test data file.')
    parser.add_argument('destination_parent_folder', help='Specify the name of the object destination file.')
    return parser.parse_args(args)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    path = os.getcwd() + '\/TradeManager\/test\/test_data\/'
    source_parent = path + args.source_parent_folder
    destination_parent = path + args.destination_parent_folder
    pickle_trade_request(source_parent, destination_parent)
    pickle_prices(source_parent, destination_parent)
    pickle_portfolios_models(source_parent)
    pickle_trade_calculator(source_parent)
    # a = read_pickle('TradeManager\/test\/test_data\/portfolio.pkl')
    # print(a)
# for b in a:
#     print(b)