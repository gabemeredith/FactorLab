"""
Tests for Rebalancer class

Test Philosophy:
- Use small, deterministic scenarios
- Hand-calculate expected trades
- Test one behavior per test

Run with: pytest tests/test_rebalancer.py -v
"""

import pytest
from datetime import date
from factorlabs.backtest.portfolio import Portfolio
from factorlabs.backtest.rebalancer import Rebalancer, Trade


# ========================== FIXTURES ==========================

@pytest.fixture
def empty_portfolio():
    """Portfolio with cash only, no positions"""
    return Portfolio(initial_cash=10000.0)


@pytest.fixture
def portfolio_with_aapl():
    """
    Portfolio with one AAPL position.

    Initial: $10,000 cash
    Bought: 50 AAPL @ $100 = $5,000
    Result: $5,000 cash + $5,000 in AAPL = $10,000 total
    """
    p = Portfolio(initial_cash=10000.0)
    p.buy(ticker="AAPL", shares=50, price=100.0, date=date(2020, 1, 1))
    return p


@pytest.fixture
def portfolio_with_two_stocks():
    """
    Portfolio with two positions.

    Initial: $10,000 cash
    Bought: 30 AAPL @ $100 = $3,000
    Bought: 50 MSFT @ $50 = $2,500
    Result: $4,500 cash + $3,000 AAPL + $2,500 MSFT = $10,000 total
    """
    p = Portfolio(initial_cash=10000.0)
    p.buy(ticker="AAPL", shares=30, price=100.0, date=date(2020, 1, 1))
    p.buy(ticker="MSFT", shares=50, price=50.0, date=date(2020, 1, 1))
    return p


# ========================== BASIC TESTS ==========================

def test_rebalance_from_cash_to_single_stock(empty_portfolio):
    """
    Test simplest case: all cash → buy one stock

    Given:
    - Cash: $10,000
    - Holdings: None
    - Total value: $10,000

    Target:
    - 100% AAPL @ $100/share

    Calculate:
    - Target AAPL value = ??? (what's 100% of $10,000?)
    - Target AAPL shares = ??? (how many shares at $100?)

    Expected:
    - 1 trade (buy)
    """
    rebalancer = Rebalancer()

    target_weights = {"AAPL": 1.0}
    prices = {"AAPL": 100.0}

    trades = rebalancer.calculate_trades(
        current_portfolio=empty_portfolio,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    # Should have exactly 1 trade
    assert len(trades) == ???  # How many trades expected?

    # Should be a buy
    trade = trades[0]
    assert trade.ticker == ???  # Which ticker?
    assert trade.side == ???  # "buy" or "sell"?
    assert trade.shares == ???  # How many shares? ($10,000 / $100)
    assert trade.price == ???  # What price?
    assert trade.date == ???  # What date?


def test_rebalance_sell_entire_position(portfolio_with_aapl):
    """
    Test selling everything

    Given:
    - Cash: $5,000
    - Holdings: 50 AAPL @ $100 (current price) = $5,000
    - Total value: $10,000

    Target:
    - 0% AAPL (sell everything)
    - 100% cash

    Calculate:
    - Target AAPL value = ??? (what's 0% of $10,000?)
    - Current AAPL shares = ??? (how many do we own?)
    - Shares to sell = ??? (how many to reach 0?)

    Expected:
    - 1 trade (sell all 50 shares)
    """
    rebalancer = Rebalancer()

    target_weights = {}  # Empty dict = 0% everything = all cash
    prices = {"AAPL": 100.0}

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_aapl,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???  # How many trades?

    trade = trades[0]
    assert trade.ticker == ???
    assert trade.side == ???  # "buy" or "sell"?
    assert trade.shares == ???  # How many shares to sell?
    assert trade.price == ???


def test_rebalance_reduce_position(portfolio_with_aapl):
    """
    Test partial sell

    Given:
    - Cash: $5,000
    - Holdings: 50 AAPL @ $100 = $5,000
    - Total value: $10,000

    Target:
    - 25% AAPL

    Calculate:
    - Target AAPL value = ??? (what's 25% of $10,000?)
    - Target AAPL shares = ??? (how many shares at $100?)
    - Current AAPL shares = 50
    - Shares to sell = ??? (50 - target shares)

    Expected:
    - Sell 25 shares (keeping 25)
    """
    rebalancer = Rebalancer()

    target_weights = {"AAPL": 0.25}  # 25% AAPL
    prices = {"AAPL": 100.0}

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_aapl,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???

    trade = trades[0]
    assert trade.ticker == ???
    assert trade.side == ???
    assert trade.shares == ???  # How many to sell? (hint: 50 current - 25 target = ?)


def test_rebalance_increase_position(portfolio_with_aapl):
    """
    Test buying more of existing position

    Given:
    - Cash: $5,000
    - Holdings: 50 AAPL @ $100 = $5,000
    - Total value: $10,000

    Target:
    - 75% AAPL

    Calculate:
    - Target AAPL value = ??? (what's 75% of $10,000?)
    - Target AAPL shares = ??? (how many shares at $100?)
    - Current AAPL shares = 50
    - Shares to buy = ??? (target - current)

    Expected:
    - Buy 25 more shares (to reach 75)
    """
    rebalancer = Rebalancer()

    target_weights = {"AAPL": 0.75}  # 75% AAPL
    prices = {"AAPL": 100.0}

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_aapl,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???

    trade = trades[0]
    assert trade.ticker == ???
    assert trade.side == ???  # "buy" or "sell"?
    assert trade.shares == ???  # How many to buy?


# ========================== MULTI-STOCK TESTS ==========================

def test_rebalance_multiple_stocks_from_cash(empty_portfolio):
    """
    Test buying multiple stocks from cash

    Given:
    - Cash: $10,000
    - Total value: $10,000

    Target:
    - 60% AAPL @ $100/share
    - 40% MSFT @ $50/share

    Calculate:
    - Target AAPL value = ??? (60% of $10,000)
    - Target AAPL shares = ??? (value / price)
    - Target MSFT value = ??? (40% of $10,000)
    - Target MSFT shares = ??? (value / price)

    Expected:
    - 2 trades (buy AAPL, buy MSFT)
    """
    rebalancer = Rebalancer()

    target_weights = {
        "AAPL": 0.6,  # 60%
        "MSFT": 0.4   # 40%
    }
    prices = {
        "AAPL": 100.0,
        "MSFT": 50.0
    }

    trades = rebalancer.calculate_trades(
        current_portfolio=empty_portfolio,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???  # How many trades?

    # Find AAPL trade
    aapl_trade = [t for t in trades if t.ticker == "AAPL"][0]
    assert aapl_trade.side == ???
    assert aapl_trade.shares == ???  # $6,000 / $100 = ?

    # Find MSFT trade
    msft_trade = [t for t in trades if t.ticker == "MSFT"][0]
    assert msft_trade.side == ???
    assert msft_trade.shares == ???  # $4,000 / $50 = ?


def test_rebalance_swap_positions(portfolio_with_aapl):
    """
    Test selling one stock to buy another

    Given:
    - Cash: $5,000
    - Holdings: 50 AAPL @ $100 = $5,000
    - Total value: $10,000

    Target:
    - 0% AAPL
    - 100% MSFT @ $50/share

    Calculate:
    - Sell AAPL: ??? shares (all of them)
    - After sell, cash = ??? ($5,000 + $5,000 from sale)
    - Buy MSFT: ??? shares ($10,000 / $50)

    Expected:
    - 2 trades: sell AAPL, then buy MSFT
    - Sells should come before buys!
    """
    rebalancer = Rebalancer()

    target_weights = {"MSFT": 1.0}  # 100% MSFT, 0% AAPL
    prices = {
        "AAPL": 100.0,
        "MSFT": 50.0
    }

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_aapl,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???  # How many trades?

    # First trade should be SELL (to free up cash)
    assert trades[0].side == ???  # Which comes first: "buy" or "sell"?
    assert trades[0].ticker == ???  # Which ticker to sell?
    assert trades[0].shares == ???

    # Second trade should be BUY
    assert trades[1].side == ???
    assert trades[1].ticker == ???
    assert trades[1].shares == ???  # $10,000 / $50 = ?


def test_rebalance_complex_multi_stock(portfolio_with_two_stocks):
    """
    Test rebalancing between multiple existing positions

    Given:
    - Cash: $4,500
    - Holdings: 30 AAPL @ $100 = $3,000
    - Holdings: 50 MSFT @ $50 = $2,500
    - Total value: $10,000

    Target:
    - 50% AAPL (currently 30%)
    - 30% MSFT (currently 25%)
    - 20% cash (currently 45%)

    Calculate:
    - Target AAPL: ??? shares (50% of $10,000 = $5,000 / $100)
    - Current AAPL: 30 shares
    - AAPL trade: ??? (buy or sell how many?)

    - Target MSFT: ??? shares (30% of $10,000 = $3,000 / $50)
    - Current MSFT: 50 shares
    - MSFT trade: ??? (buy or sell how many?)

    Expected:
    - Sell some MSFT
    - Buy some AAPL
    - Order matters! (sells first)
    """
    rebalancer = Rebalancer()

    target_weights = {
        "AAPL": 0.5,   # 50%
        "MSFT": 0.3    # 30% (20% will be cash automatically)
    }
    prices = {
        "AAPL": 100.0,
        "MSFT": 50.0
    }

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_two_stocks,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    # Should have 2 trades
    assert len(trades) == ???

    # Find MSFT trade (should be first because it's a sell)
    msft_trade = [t for t in trades if t.ticker == "MSFT"][0]
    assert msft_trade.side == ???  # buy or sell?
    assert msft_trade.shares == ???  # Current 50, target 60, so trade = ?

    # Find AAPL trade
    aapl_trade = [t for t in trades if t.ticker == "AAPL"][0]
    assert aapl_trade.side == ???  # buy or sell?
    assert aapl_trade.shares == ???  # Current 30, target 50, so trade = ?


# ========================== EDGE CASES ==========================

def test_rebalance_no_changes_needed(portfolio_with_aapl):
    """
    Test when portfolio already matches target weights

    Given:
    - Cash: $5,000 (50%)
    - Holdings: 50 AAPL @ $100 = $5,000 (50%)

    Target:
    - 50% AAPL

    Expected:
    - No trades needed!
    """
    rebalancer = Rebalancer()

    target_weights = {"AAPL": 0.5}  # Already at 50%
    prices = {"AAPL": 100.0}

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_aapl,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???  # Should be 0 (no trades needed)


def test_rebalance_with_price_change(portfolio_with_aapl):
    """
    Test when current price differs from entry price

    Given:
    - Cash: $5,000
    - Holdings: 50 AAPL bought @ $100, but now worth $200/share
    - Current holdings value: 50 * $200 = $10,000
    - Total value: $15,000

    Target:
    - 50% AAPL

    Calculate:
    - Target AAPL value = ??? (50% of $15,000)
    - Target AAPL shares = ??? ($7,500 / $200)
    - Current shares = 50
    - Trade = ??? (sell how many?)

    Expected:
    - Sell some AAPL (it's grown beyond 50%)
    """
    rebalancer = Rebalancer()

    target_weights = {"AAPL": 0.5}  # 50% AAPL
    prices = {"AAPL": 200.0}  # Price has doubled!

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_aapl,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???

    trade = trades[0]
    assert trade.side == ???  # buy or sell?
    assert trade.shares == ???  # Current 50, target ?, trade = ?
    assert trade.price == ???  # Use current price, not entry price!


def test_rebalance_empty_target_weights(portfolio_with_two_stocks):
    """
    Test selling everything (go to 100% cash)

    Given:
    - Some stocks

    Target:
    - {} (empty dict = all cash)

    Expected:
    - Sell everything
    """
    rebalancer = Rebalancer()

    target_weights = {}  # Sell everything
    prices = {
        "AAPL": 100.0,
        "MSFT": 50.0
    }

    trades = rebalancer.calculate_trades(
        current_portfolio=portfolio_with_two_stocks,
        target_weights=target_weights,
        prices=prices,
        trade_date=date(2020, 1, 2)
    )

    assert len(trades) == ???  # How many positions to close?

    # Both should be sells
    assert all(t.side == ??? for t in trades)

    # Find each ticker
    aapl_trade = [t for t in trades if t.ticker == "AAPL"][0]
    assert aapl_trade.shares == ???  # Sell all 30 shares

    msft_trade = [t for t in trades if t.ticker == "MSFT"][0]
    assert msft_trade.shares == ???  # Sell all 50 shares