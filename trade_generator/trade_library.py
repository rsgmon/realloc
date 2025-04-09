from typing import List, Optional, Dict
import math

def sell_position(current: float, target: float) -> float:
    """
    Calculates the amount to sell from a single position.

    :param current: The current amount held.
    :param target: The target amount to hold.
    :return: The amount to sell (0 if no selling is needed).
    """
    return max(current - target, 0)

def calculate_sell_amounts(current_amounts: List[float], target_amounts: List[Optional[float]]) -> List[float]:
    """
    Calculates sell amounts for a list of positions.

    :param current_amounts: The list of current amounts held.
    :param target_amounts: The list of target amounts.
    :return: The list of sell amounts for each position.
    """
    sell_amounts = []
    for i, current in enumerate(current_amounts):
        target = target_amounts[i] if i < len(target_amounts) and target_amounts[i] is not None else 0
        sell = sell_position(current, target)
        sell_amounts.append(sell)
    return sell_amounts

def buy_position(current: float, target: float) -> float:
    """
    Calculates the amount to buy for a single position.

    :param current: The current amount held.
    :param target: The target amount to hold.
    :return: The amount to buy (0 if no buying is needed).
    """
    return max(target - current, 0)

def calculate_buy_amounts(current_amounts: List[float], target_amounts: List[Optional[float]]) -> List[float]:
    """
    Calculates buy amounts for a list of positions.

    :param current_amounts: The list of current amounts held.
    :param target_amounts: The list of target amounts.
    :return: The list of buy amounts for each position.
    """
    buy_amounts = []
    for i, current in enumerate(current_amounts):
        target = target_amounts[i] if i < len(target_amounts) and target_amounts[i] is not None else 0
        buy = buy_position(current, target)
        buy_amounts.append(buy)
    return buy_amounts

def get_mock_prices(symbols: List[str]) -> Dict[str, float]:
    """
    Mock price service that returns a fixed price per symbol.

    :param symbols: List of investment symbols.
    :return: Dictionary mapping symbol to price.
    """
    return {symbol: 100.0 + i * 5 for i, symbol in enumerate(symbols)}

def calculate_buy_share_amounts(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None
) -> Dict[str, int]:
    current_shares, target_shares = normalize_symbol_sets(current_shares, target_shares)
    symbols = list(current_shares.keys())

    if prices is None:
        prices = get_mock_prices(symbols)

    current_dollars = [current_shares[symbol] * prices[symbol] for symbol in symbols]
    target_dollars = [target_shares[symbol] * prices[symbol] for symbol in symbols]
    buy_dollars = [buy_position(current, target) for current, target in zip(current_dollars, target_dollars)]

    return {
        symbol: int(math.floor(buy_dollars[i] / prices[symbol]))
        for i, symbol in enumerate(symbols)
    }

def calculate_sell_share_amounts(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None
) -> Dict[str, int]:
    current_shares, target_shares = normalize_symbol_sets(current_shares, target_shares)
    symbols = list(current_shares.keys())

    if prices is None:
        prices = get_mock_prices(symbols)

    current_dollars = [current_shares[symbol] * prices[symbol] for symbol in symbols]
    target_dollars = [target_shares[symbol] * prices[symbol] for symbol in symbols]
    sell_dollars = [sell_position(current, target) for current, target in zip(current_dollars, target_dollars)]

    return {
        symbol: int(math.floor(sell_dollars[i] / prices[symbol]))
        for i, symbol in enumerate(symbols)
    }

def normalize_symbol_sets(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float]
) -> (Dict[str, float], Dict[str, float]):
    all_symbols = set(current_shares.keys()) | set(target_shares.keys())
    return (
        {symbol: current_shares.get(symbol, 0.0) for symbol in all_symbols},
        {symbol: target_shares.get(symbol, 0.0) for symbol in all_symbols}
    )

def allocate_trades(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None
) -> Dict[str, int]:
    """
    Unified allocator that returns net trade shares per symbol to reach target.

    :param current_shares: Dictionary of current shares per symbol.
    :param target_shares: Dictionary of target shares per symbol.
    :param prices: Optional dictionary of prices per symbol. If None, mock prices are used.
    :return: Dictionary of symbol -> net trade shares (positive to buy, negative to sell).
    """
    current_shares, target_shares = normalize_symbol_sets(current_shares, target_shares)
    symbols = list(current_shares.keys())

    if prices is None:
        prices = get_mock_prices(symbols)

    return {
        symbol: int(math.floor(target_shares[symbol] - current_shares[symbol]))
        for symbol in symbols
    }

def split_trades(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None
) -> Dict[str, Dict[str, int]]:
    """
    Splits the unified trade allocation into separate buy and sell orders.

    :param current_shares: Dictionary of current shares per symbol.
    :param target_shares: Dictionary of target shares per symbol.
    :param prices: Optional dictionary of prices per symbol.
    :return: Dictionary with 'buy' and 'sell' keys containing symbol -> share mappings.
    """
    net_trades = allocate_trades(current_shares, target_shares, prices)
    buys = {symbol: shares for symbol, shares in net_trades.items() if shares > 0}
    sells = {symbol: abs(shares) for symbol, shares in net_trades.items() if shares < 0}
    return {'buy': buys, 'sell': sells}
