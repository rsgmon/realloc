from typing import List, Dict


def get_mock_prices(symbols: List[str]) -> Dict[str, float]:
    """
    Mock price service that returns a fixed price per symbol.
    """
    return {symbol: 100.0 + i * 5 for i, symbol in enumerate(symbols)}
