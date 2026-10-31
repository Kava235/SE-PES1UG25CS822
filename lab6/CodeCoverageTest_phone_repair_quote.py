import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600


def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1


def test_unknown_part():
    with pytest.raises(ValueError):
        repair_quote("speaker", "budget", False, False)


def test_unknown_tier():
    with pytest.raises(ValueError):
        repair_quote("screen", "midrange", False, False)


def test_flagship_screen_express():
    assert repair_quote("screen", "flagship", False, True) == 9100


def test_battery_warranty():
    assert repair_quote("battery", "budget", True, False) == 300


def test_days_screen_oos_no_tech():
    assert repair_days("screen", False, 0) == 8


def test_days_battery_oos():
    assert repair_days("battery", False, 2) == 3


def test_trade_in_invalid():
    with pytest.raises(ValueError):
        trade_in_value(0, 10, False)


def test_trade_in_too_old():
    assert trade_in_value(10000, 60, False) == 0


def test_trade_in_new():
    assert trade_in_value(10000, 6, False) == 6000


def test_trade_in_mid():
    assert trade_in_value(10000, 18, False) == 4000


def test_trade_in_old_cracked():
    assert trade_in_value(10000, 30, True) == 1000