import logging
from typing import Dict, List

from realloc import Trade, PortfolioStateManager
from realloc.plugins.core.base import RebalancerPlugin
from realloc import (
    select_account_for_buy_trade,
    select_account_for_sell_trade,
    is_trade_remaining,
)

logger = logging.getLogger(__name__)

MIN_TRADE_QTY = 1

class DefaultRebalancer(RebalancerPlugin):
    """Default implementation of the rebalancer plugin"""

    @property
    def name(self) -> str:
        return "default"

    def execute_rebalance(
            self,
            portfolio_state: PortfolioStateManager,
            target_shares: Dict[str, float],
            max_iterations: int
    ) -> List[Trade]:
        iteration = 0
        account_trades = []

        while is_trade_remaining(portfolio_state.portfolio_trades) and iteration < max_iterations:
            sorted_trades = sorted(
                portfolio_state.portfolio_trades.items(),
                key=lambda item: (item[1] > 0, abs(item[1]))
            )
            made_trade = False

            for symbol, qty in sorted_trades:
                direction = "buy" if qty > 0 else "sell"
                qty_remaining = abs(qty)

                account_id = (
                    select_account_for_buy_trade(
                        symbol,
                        qty_remaining,
                        list(portfolio_state.accounts.values()),
                        portfolio_state.prices,
                        portfolio_state.cash_matrix,
                    )
                    if direction == "buy"
                    else select_account_for_sell_trade(
                        symbol, qty_remaining, list(portfolio_state.accounts.values())
                    )
                )

                if account_id is None:
                    logger.warning(f"Cannot find account to {direction} {qty_remaining} {symbol}")
                    continue

                account = portfolio_state.accounts[account_id]
                if direction == "buy":
                    max_affordable = int(portfolio_state.cash_matrix[account_id] // portfolio_state.prices[symbol])
                    qty_to_trade = min(qty_remaining, max_affordable)
                else:
                    qty_to_trade = min(qty_remaining, int(account.positions.get(symbol, 0)))

                if qty_to_trade == 0:
                    continue

                trade_qty = qty_to_trade if direction == "buy" else -qty_to_trade
                single_trade = Trade(account_id, symbol, trade_qty)
                account_trades.append(single_trade)

                logger.info(
                    f"Executing {direction} of {qty_to_trade} {symbol} in account {account_id}"
                )

                portfolio_state.update([single_trade])
                portfolio_state.update_portfolio_trades(target_shares)
                made_trade = True

            if not made_trade:
                # If we couldn't make any trades in this iteration, break to avoid infinite loop
                break

            iteration += 1

        if iteration >= max_iterations:
            logger.warning("Max iterations reached. Some trades may be unresolved.")

        return account_trades