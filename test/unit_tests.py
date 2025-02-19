import pytest
import json
import pandas as pd
from trade_generator.trade_manager import TradeManager, TradeRequest, Model, Prices, RawRequest
from trade_generator.allocation import TradeAccountMatrix, MultipleAccountTradeSelector, TradeInstructions, TradingLibrary
from trade_generator.trade_calculator import TradeCalculator
from trade_generator.portfolio import Portfolio
from test_data_generator import read_pickle


@pytest.fixture
def sample_raw_request():
    return RawRequest('test', {
        "data": {"symbol": ["SPY", "MDY"], "price": [100, 280], "account_number": ["123-45", "123-45"],
                 "shares": [30, 50], "restrictions": [None, None], "model_weight": [0.5, 0.5]}
    })

@pytest.fixture
def sample_trade_request(sample_raw_request):
    return TradeRequest(sample_raw_request)

@pytest.fixture
def sample_prices(sample_raw_request):
    return Prices(sample_raw_request)

@pytest.fixture
def sample_portfolio(sample_trade_request, sample_prices):
    return Portfolio(sample_trade_request.portfolio_request, sample_prices.prices)

@pytest.fixture
def sample_model(sample_trade_request):
    return Model(sample_trade_request.model_request)

@pytest.fixture
def sample_trade_calculator(sample_portfolio, sample_model, sample_prices):
    return TradeCalculator(sample_portfolio, sample_model, sample_prices.prices)


def test_raw_request_missing_columns():
    with pytest.raises(RuntimeError, match='The following columns were missing: .*'):
        RawRequest('test', {"data": {"symbol": ["A"]}, "index": ["model"]})._missing_required_columns()


def test_trade_request(sample_trade_request):
    assert not sample_trade_request.portfolio_request.empty, "Portfolio request should not be empty"
    assert not sample_trade_request.model_request.empty, "Model request should not be empty"


def test_portfolio_initialization(sample_portfolio):
    assert sample_portfolio.portfolio_value > 0, "Portfolio value should be positive"
    assert sample_portfolio.portfolio_cash >= 0, "Portfolio cash should be non-negative"


def test_trade_calculator_buy_only(sample_trade_calculator):
    assert 'SPY' in sample_trade_calculator.portfolio_trade_list.index, "Trade calculator should generate trades for SPY"
    assert sample_trade_calculator.portfolio_trade_list.loc['SPY', 'share_trades'] > 0, "Trade should be a buy order"


def test_trade_manager(sample_trade_request):
    trade_manager = TradeManager('test', sample_trade_request.raw_request)
    assert not trade_manager.trade_instructions.empty, "Trade instructions should be generated"


@pytest.mark.parametrize("symbol, expected_value", [
    ("SPY", 30),
    ("MDY", 50)
])
def test_portfolio_positions(sample_portfolio, symbol, expected_value):
    assert sample_portfolio.portfolio_positions.loc[symbol, 'shares'] == expected_value, f"Expected {expected_value} shares for {symbol}"
