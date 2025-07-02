import pytest
from realloc import (
    Account,
    select_account_for_buy_trade,
    select_account_for_sell_trade,
    TaxAwareSelector,
)


@pytest.fixture
def accounts():
    return [
        Account("A", "A001", 1000, {"AAPL": 5}, {}),
        Account("B", "A002", 2000, {"GOOG": 10}, {}),
    ]


@pytest.fixture
def accounts_with_cash_and_positions():
    return [
        Account("Taxable1", "T001", 5000, {"AAPL": 20}, {}),
        Account("IRA1", "D001", 10000, {"AAPL": 5, "GOOG": 15}, {}),
        Account("IRA2", "D002", 8000, {"MSFT": 10}, {}),
    ]


# --------------------------------------------------------
# 🔥 Tests for Basic Selectors
# --------------------------------------------------------


def test_select_account_for_buy_trade_existing_holder(accounts):
    cash_matrix = {a.account_number: a.cash for a in accounts}
    prices = {"AAPL": 100, "GOOG": 200}
    selected = select_account_for_buy_trade("AAPL", 3, accounts, prices, cash_matrix)
    assert selected == "A001"


def test_select_account_for_buy_trade_fallback_to_cash(accounts):
    cash_matrix = {a.account_number: a.cash for a in accounts}
    prices = {"MSFT": 100}
    selected = select_account_for_buy_trade("MSFT", 5, accounts, prices, cash_matrix)
    assert selected == "A001"


def test_select_account_for_sell_trade_full_sell(accounts):
    selected = select_account_for_sell_trade("GOOG", 5, accounts)
    assert selected == "A002"


def test_select_account_for_sell_trade_partial(accounts):
    selected = select_account_for_sell_trade("AAPL", 10, accounts)
    assert selected == "A001"


def test_select_account_for_sell_trade_none():
    accounts = [Account("C", "A003", 500, {}, {})]
    selected = select_account_for_sell_trade("TSLA", 1, accounts)
    assert selected is None


# --------------------------------------------------------
# ✨ New Tests: TaxAwareSelector
# --------------------------------------------------------


def test_taxawareselector_prefers_taxable_sells(accounts_with_cash_and_positions):
    selector = TaxAwareSelector(tax_deferred_accounts=["D001", "D002"])

    selected = selector.select_account_for_sell_trade(
        "AAPL", 5, accounts_with_cash_and_positions
    )
    assert selected == "T001"  # taxable account first


def test_taxawareselector_fallback_to_deferred(accounts_with_cash_and_positions):
    selector = TaxAwareSelector(tax_deferred_accounts=["D001", "D002"])

    # Sell MSFT, which only deferred accounts have
    selected = selector.select_account_for_sell_trade(
        "MSFT", 5, accounts_with_cash_and_positions
    )
    assert selected == "D002"


def test_taxawareselector_buy_prefers_deferred(accounts_with_cash_and_positions):
    selector = TaxAwareSelector(tax_deferred_accounts=["D001", "D002"])
    prices = {"AAPL": 100, "GOOG": 200, "MSFT": 100}
    cash_matrix = {a.account_number: a.cash for a in accounts_with_cash_and_positions}

    selected = selector.select_account_for_buy_trade(
        "AAPL", 10, accounts_with_cash_and_positions, prices, cash_matrix
    )
    assert selected in ["D001", "D002"]


def test_taxawareselector_fallback_to_taxable(accounts_with_cash_and_positions):
    selector = TaxAwareSelector(tax_deferred_accounts=["D001", "D002"])
    prices = {"XYZ": 100}  # Non-held symbol
    cash_matrix = {a.account_number: a.cash for a in accounts_with_cash_and_positions}

    selected = selector.select_account_for_buy_trade(
        "XYZ", 10, accounts_with_cash_and_positions, prices, cash_matrix
    )
    assert selected is not None  # Should select anyone with enough cash


def test_taxawareselector_no_accounts_can_buy(accounts_with_cash_and_positions):
    selector = TaxAwareSelector(tax_deferred_accounts=["D001", "D002"])
    prices = {"AAPL": 50000}  # Way too expensive
    cash_matrix = {a.account_number: a.cash for a in accounts_with_cash_and_positions}

    selected = selector.select_account_for_buy_trade(
        "AAPL", 1, accounts_with_cash_and_positions, prices, cash_matrix
    )
    assert selected is None


# --------------------------------------------------------
# 🛠 Corner Cases
# --------------------------------------------------------


def test_select_account_for_buy_trade_no_cash(accounts):
    cash_matrix = {a.account_number: 0 for a in accounts}
    prices = {"AAPL": 100, "GOOG": 200}
    selected = select_account_for_buy_trade("AAPL", 1, accounts, prices, cash_matrix)
    assert selected is None


def test_select_account_for_sell_trade_empty_accounts():
    selected = select_account_for_sell_trade("AAPL", 5, [])
    assert selected is None
