import TradeManager.test.test_data.test_data as test_data
import TradeManager.allocation as allocate
import TradeManager.portfolio as portfolio
import TradeManager.trade_calculator as tc
import TradeManager.trade_manager as trade_manage
import pickle


def pickle_portfolios_models():
    # trade_requests = [trade_manage.TradeRequest(test_data.trade_requests[value]) for value in test_data.trade_requests]
    mocks = {}
    for request in test_data.trade_requests:
        mock = {}
        mock['request'] = trade_manage.TradeRequest(test_data.trade_requests[request])
        mock['portfolio'] = portfolio.Portfolio(mock['request'].portfolio_request)
        mock['model'] = trade_manage.Model(mock['request'].model_request)
        mocks[request] = mock
    with open('mocks.pkl', 'wb') as myfile:
        pickle.dump(mocks, myfile)

def pickle_trade_calculator():
    mocks = read_pickle('mocks.pkl')
    for mock in mocks:
        mocks[mock]['trade_calculator'] = tc.TradeCalculator(mocks[mock]['portfolio'], mocks[mock]['model'])
    with open('mocks.pkl', 'wb') as myfile:
        pickle.dump(mocks, myfile)

def read_pickle(file):
    with open(file, 'rb') as afile:
        apickle = pickle.load(afile)
    return apickle

pickle_portfolios_models()
pickle_trade_calculator()
# a = read_pickle('mocks.pkl')
# for b in a:
#     print(b)