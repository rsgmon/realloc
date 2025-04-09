import pytest
from portmgr import sell_position, calculate_sell_amounts, buy_position, calculate_buy_amounts

def test_sell_position():
    assert sell_position(100, 80) == 20
    assert sell_position(80, 100) == 0
    assert sell_position(100, 100) == 0

def test_calculate_sell_amounts():
    current = [100, 200, 150]
    target = [90, 250, None]
    expected = [10, 0, 150]
    assert calculate_sell_amounts(current, target) == expected

def test_buy_position():
    assert buy_position(100, 120) == 20
    assert buy_position(120, 100) == 0
    assert buy_position(100, 100) == 0

def test_calculate_buy_amounts():
    current = [100, 200, 150]
    target = [120, 150, None]
    expected = [20, 0, 0]
    assert calculate_buy_amounts(current, target) == expected
