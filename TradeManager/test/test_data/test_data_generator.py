# import TradeManager.allocation as allocate
import TradeManager.portfolio as portfolio
import TradeManager.trade_calculator as tc
import TradeManager.trade_manager as trade_manage
import pickle
import argparse
import sys

def pickle_trade_request(file_path):
    mocks = trade_manage.TradeRequest(trade_manage.RawRequest(read_pickle('excel_request.pkl'), file_path))
    with open('request.pkl', 'wb') as myfile:
        pickle.dump(mocks, myfile)

def pickle_prices(file_path):
    prices = trade_manage.PriceRetriever(trade_manage.RawRequest(read_pickle('excel_request.pkl'), file_path))
    prices()
    with open('prices.pkl', 'wb') as myprices:
        pickle.dump(prices, myprices)

def pickle_portfolios_models():
    treq = read_pickle('request.pkl')
    prices = read_pickle('prices.pkl')
    port = portfolio.Portfolio(treq.portfolio_request, prices.prices)

    with open('portfolio.pkl', 'wb') as myfile:
        pickle.dump(port, myfile)

def pickle_trade_calculator():
    portfolio = read_pickle('portfolio.pkl')
    trade_request = read_pickle('request.pkl')
    prices = read_pickle('prices.pkl')
    model = trade_request.model_request
    trade_calculator = tc.TradeCalculator(portfolio, model, prices)
    with open('trade_list.pkl', 'wb') as myfile:
        pickle.dump(trade_calculator, myfile)

def read_pickle(file):
    with open(file, 'rb') as afile:
        apickle = pickle.load(afile)
    return apickle

def _parse_args(args=None):
    if not args: return None
    parser = argparse.ArgumentParser(description='Path to the config file.')
    parser.add_argument('path', help='Specify the absolute path of the config file.')
    parser.add_argument('--destination_path', help='S')
    return parser.parse_args(args)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    pickle_trade_request(args.path)
    # pickle_prices('Trade Request Example.xlsx')
    # pickle_portfolios_models()
    # pickle_trade_calculator()
# a = read_pickle('portfolio.pkl')
# print(a)
# for b in a:
#     print(b)