"""
Tests for Portfolio enhancements (Phase 2).

Testing:
- get_unrealized_pnl() - paper gains/losses on open positions
- get_realized_pnl() - actual gains/losses from sales
- get_positions_df() - export positions as DataFrame
- get_holdings_value() - current market value per ticker
"""

import sys
sys.path.insert(0, 'src')

import pytest
from datetime import date
from factorlabs.backtest.portfolio import Portfolio


# ========================== UNREALIZED P&L TESTS ==========================

def test_unrealized_pnl_single_position_gain():
    """
    Test unrealized P&L for a single position with gain.

    Given: Buy 100 shares AAPL at $150
    When: Current price is $160
    Then: Unrealized P&L = ???

    YOUR CALCULATION:
    - Cost basis = 100 × $150 = $15,000
    - Current value = 100 × $160 = $16,000
    - Unrealized P&L = $16,000 - $15,000 = $1,000
    """
    portfolio = Portfolio(initial_cash=100000.0)
    portfolio.buy("AAPL", 100.0, 150.0, date(2020, 1, 1))

    current_prices = {"AAPL": 160.0}
    unrealized = portfolio.get_unrealized_pnl(current_prices)

    assert unrealized == 1000.0


def test_unrealized_pnl_single_position_loss():
    """
    Test unrealized P&L for a single position with loss.

    Given: Buy 100 shares AAPL at $150
    When: Current price is $140
    Then: Unrealized P&L = ???

    YOUR TURN: Calculate the expected value!
    - Cost basis = ?
    - Current value = ?
    - Unrealized P&L = ?
    """
    portfolio = Portfolio(initial_cash=100000.0)
    portfolio.buy("AAPL", 100.0, 150.0, date(2020, 1, 1))

    current_prices = {"AAPL": 140.0}
    unrealized = portfolio.get_unrealized_pnl(current_prices)

    # TODO: Replace ??? with your hand-calculated value
    assert unrealized == -1000


def test_unrealized_pnl_multiple_positions():
    """
    Test unrealized P&L across multiple positions.

    Given:
    - Buy 100 AAPL at $150
    - Buy 50 MSFT at $200
    When:
    - AAPL price = $160 (gain)
    - MSFT price = $190 (loss)
    Then: Total unrealized P&L = ???

    YOUR TURN: Calculate!
    - AAPL: cost = ?, value = ?, P&L = ?
    - MSFT: cost = ?, value = ?, P&L = ?
    - Total P&L = ?
    """
    portfolio = Portfolio(initial_cash=100000.0)
    portfolio.buy("AAPL", 100.0, 150.0, date(2020, 1, 1))
    portfolio.buy("MSFT", 50.0, 200.0, date(2020, 1, 1))

    current_prices = {"AAPL": 160.0, "MSFT": 190.0}
    unrealized = portfolio.get_unrealized_pnl(current_prices)

    # TODO: Replace ??? with your hand-calculated value
    assert unrealized == 500


def test_unrealized_pnl_no_positions():
    """
    Test unrealized P&L when portfolio has no positions.

    Given: Empty portfolio (only cash)
    When: No positions held
    Then: Unrealized P&L = ???

    YOUR TURN: What should this be?
    """
    portfolio = Portfolio(initial_cash=100000.0)

    current_prices = {}
    unrealized = portfolio.get_unrealized_pnl(current_prices)

    # TODO: Replace ??? with your hand-calculated value
    assert unrealized == 0


def test_unrealized_pnl_after_averaging_up():
    """
    Test unrealized P&L after buying more shares (averaging up).

    Given:
    - Buy 100 AAPL at $150 (cost = $15,000)
    - Buy 100 more AAPL at $160 (cost = $16,000)
    - Average cost basis = $31,000 / 200 = $155
    When: Current price = $170
    Then: Unrealized P&L = ???

    YOUR TURN: Calculate!
    - Total shares = ?
    - Average cost basis = ?
    - Total cost = ?
    - Current value = ?
    - Unrealized P&L = ?
    """
    portfolio = Portfolio(initial_cash=100000.0)
    portfolio.buy("AAPL", 100.0, 150.0, date(2020, 1, 1))
    portfolio.buy("AAPL", 100.0, 160.0, date(2020, 1, 5))

    current_prices = {"AAPL": 170.0}
    unrealized = portfolio.get_unrealized_pnl(current_prices)

    # TODO: Replace ??? with your hand-calculated value
    assert unrealized == 3000


def test_unrealized_pnl_missing_price():
    """
    Test unrealized P&L when current price is missing.

    Given: Hold 100 AAPL
    When: Price data doesn't include AAPL
    Then: Unrealized P&L = ???

    Hint: If we don't have a price, we can't calculate P&L.
    What's a reasonable default? Should we:
    - Assume price = 0? (P&L = -cost_basis)
    - Skip the position? (P&L = 0 for that position)
    - Raise an error?

    YOUR DECISION: Choose the most sensible behavior.
    """
    portfolio = Portfolio(initial_cash=100000.0)
    portfolio.buy("AAPL", 100.0, 150.0, date(2020, 1, 1))

    current_prices = {}  # No AAPL price!
    unrealized = portfolio.get_unrealized_pnl(current_prices)

    # Option B: Skip position if price missing (forgiving approach)
    # If we can't get the price, we can't calculate P&L for that position
    # So we treat it as 0 contribution to total unrealized P&L
    assert unrealized == 0.0