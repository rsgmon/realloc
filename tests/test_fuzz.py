import pytest
from hypothesis import given, strategies as st
from realloc import (
    Account,
    PortfolioModel,
    PortfolioAllocator,
    PortfolioStateManager,
    select_account_for_buy_trade, Trade,
)


# --------------------------------------------------------
# 🔥 Fuzz TAM: No Negative Positions
# --------------------------------------------------------


@given(
    cash=st.floats(min_value=500, max_value=10000),
    initial_shares=st.integers(min_value=0, max_value=50),
    trade_shares=st.integers(min_value=-50, max_value=50),
    price=st.floats(min_value=1, max_value=500),
)
def test_portfolio_state_manager_no_negative_position(
    cash, initial_shares, trade_shares, price
):
    acc = Account(
        label="Test",
        account_number="T1",
        cash=cash,
        positions={"AAPL": initial_shares},
        enforce_no_negative_positions=True,
    )
    tam = PortfolioStateManager([acc], {"AAPL": price})
    trade = Trade("T1", "AAPL", trade_shares)

    if initial_shares + trade_shares < 0:
        with pytest.raises(ValueError):
            tam.update([trade])
    else:
        tam.update([trade])
        assert acc.positions["AAPL"] >= 0


# --------------------------------------------------------
# 🔥 Fuzz Selectors: Always Valid Pick
# --------------------------------------------------------


@given(
    account_cash=st.lists(
        st.floats(min_value=0, max_value=10000), min_size=2, max_size=5
    ),
    share_qty=st.lists(st.integers(min_value=0, max_value=100), min_size=2, max_size=5),
    price=st.floats(min_value=10, max_value=1000),
)
def test_selector_picks_valid_account(account_cash, share_qty, price):
    accounts = []
    for idx, (cash, qty) in enumerate(zip(account_cash, share_qty)):
        accounts.append(
            Account(
                label=f"Test{idx}",
                account_number=f"A{idx}",
                cash=cash,
                positions={"AAPL": qty},
            )
        )
    cash_matrix = {a.account_number: a.cash for a in accounts}
    prices = {"AAPL": price}
    trade_amount = 5

    selected = select_account_for_buy_trade(
        "AAPL", trade_amount, accounts, prices, cash_matrix
    )

    if selected:
        selected_account = next(
            acc for acc in accounts if acc.account_number == selected
        )
        assert cash_matrix[selected_account.account_number] >= price
