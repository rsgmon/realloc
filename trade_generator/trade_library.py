from typing import List, Optional

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
