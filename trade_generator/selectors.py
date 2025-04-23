from typing import List, Optional, Dict

from trade_generator.accounts import Account


def select_account_for_buy_trade(
    symbol: str,
    trade_amount: int,
    accounts: List[Account],
    prices: Dict[str, float],
    cash_matrix: Dict[str, float]
) -> Optional[str]:
    """
    Select the most appropriate account for a buy trade based on strict priority:
    1. Holder who can fully fulfill
    2. Holder who can partially fulfill (largest partial)
    3. Non-holder who can fully fulfill
    4. Non-holder who can partially fulfill (largest partial)
    """
    price = prices[symbol]

    # Step 1: Holder who can fully fulfill
    holder_full = [
        a for a in accounts
        if symbol in a.positions and int(cash_matrix[a.account_number] // price) >= trade_amount
    ]
    if holder_full:
        return holder_full[0].account_number  # highest position not required — any is fine

    # Step 2: Holder who can partially fulfill
    holder_partials = [
        (a, int(cash_matrix[a.account_number] // price))
        for a in accounts
        if symbol in a.positions and int(cash_matrix[a.account_number] // price) > 0
    ]
    if holder_partials:
        best = max(holder_partials, key=lambda x: x[1])
        return best[0].account_number

    # Step 3: Non-holder who can fully fulfill
    nonholder_full = [
        a for a in accounts
        if symbol not in a.positions and int(cash_matrix[a.account_number] // price) >= trade_amount
    ]
    if nonholder_full:
        return nonholder_full[0].account_number

    # Step 4: Non-holder who can partially fulfill
    nonholder_partials = [
        (a, int(cash_matrix[a.account_number] // price))
        for a in accounts
        if symbol not in a.positions and int(cash_matrix[a.account_number] // price) > 0
    ]
    if nonholder_partials:
        best = max(nonholder_partials, key=lambda x: x[1])
        return best[0].account_number

    return None


def select_account_for_sell_trade(
    symbol: str,
    trade_amount: int,
    accounts: List[Account]
) -> Optional[str]:
    """
    Select the most appropriate account for a given sell trade.

    Priority:
    1. Accounts that already hold the symbol.
    2. Among them, the one with the largest position.
    3. Return the first one that can fulfill the full sell.
    4. If none can do it fully, choose the one that can do the largest partial.
    """
    candidates = [a for a in accounts if symbol in a.positions and a.positions[symbol] > 0]
    if not candidates:
        return None

    candidates.sort(key=lambda a: a.positions.get(symbol, 0), reverse=True)
    for account in candidates:
        if account.positions[symbol] >= trade_amount:
            return account.account_number

    # Fallback to the one with the largest position
    return candidates[0].account_number if candidates else None