"""
Backtester - Orchestrates portfolio simulation over time

This module ties together the Portfolio, Rebalancer, and price data
to simulate a trading strategy over a historical period.

Key responsibilities:
- Run time loop (day by day)
- Get prices for each date
- Calculate required trades (using Rebalancer)
- Execute trades (using Portfolio)
- Record state (equity curve, trades, positions)
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Literal
import polars as pl

from .portfolio import Portfolio
from .rebalancer import Rebalancer


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""
    start_date: date
    end_date: date
    initial_cash: float
    rebalance_frequency: Literal["daily", "weekly", "monthly", "never"] = "daily"
    transaction_cost: float = 0.0  # basis points (e.g., 10 = 0.1%)


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    equity_curve: pl.DataFrame      # Columns: date, portfolio_value, cash, positions_value
    trades: pl.DataFrame            # Columns: date, ticker, shares, price, side
    positions_history: pl.DataFrame = None  # Optional: date, ticker, shares, value
    metrics: dict = field(default_factory=dict)  # Summary metrics (total return, etc.)


class Backtester:
    """
    Runs portfolio simulations over historical price data.

    The backtester implements an explicit time loop:
    1. For each date in the simulation period:
       a. Get prices for that date
       b. Calculate target trades (using Rebalancer)
       c. Execute trades (using Portfolio)
       d. Record portfolio state
    2. Return results as DataFrames

    This design prioritizes:
    - Clarity: Explicit day-by-day execution (no hidden vectorization)
    - Correctness: Realistic trade sequencing
    - Auditability: Every state change is recorded
    """

    def run(
        self,
        prices: pl.DataFrame,
        target_weights: dict[str, float],
        config: BacktestConfig
    ) -> BacktestResult:
        """
        Run a backtest simulation.

        Algorithm:
        1. Initialize Portfolio with config.initial_cash
        2. Initialize Rebalancer
        3. Get list of dates from config.start_date to config.end_date
        4. For each date:
           a. Get prices for that date (from prices DataFrame)
           b. Check if should rebalance (based on rebalance_frequency)
           c. If rebalancing:
              - Calculate trades using rebalancer.calculate_trades()
              - Execute each trade using portfolio.buy() or portfolio.sell()
              - Record the trades
           d. Record portfolio state (cash, positions, total value)
        5. Build equity_curve DataFrame
        6. Build trades DataFrame
        7. Return BacktestResult

        Parameters
        ----------
        prices : pl.DataFrame
            Historical prices with columns: date, ticker, close
            Should contain all dates and tickers needed for the backtest
        target_weights : dict[str, float]
            Target allocation (ticker → weight)
            For now, this is static (same weights every rebalance)
            Later: will be replaced by Strategy object
        config : BacktestConfig
            Backtest parameters (dates, cash, frequency, etc.)

        Returns
        -------
        BacktestResult
            Contains equity_curve, trades, and other results

        Examples
        --------
        >>> prices = pl.DataFrame({
        ...     "date": [date(2020, 1, 1), date(2020, 1, 2)],
        ...     "ticker": ["AAPL", "AAPL"],
        ...     "close": [100.0, 110.0]
        ... })
        >>> config = BacktestConfig(
        ...     start_date=date(2020, 1, 1),
        ...     end_date=date(2020, 1, 2),
        ...     initial_cash=10000.0
        ... )
        >>> backtester = Backtester()
        >>> result = backtester.run(
        ...     prices=prices,
        ...     target_weights={"AAPL": 1.0},
        ...     config=config
        ... )
        >>> len(result.equity_curve)  # Should have 2 rows
        2
        """
        # TODO: Implement this!
        # Hints:
        # 1. Initialize Portfolio and Rebalancer
        # 2. Get list of unique dates from prices DataFrame
        # 3. Filter dates to config.start_date and config.end_date
        # 4. Loop through each date:
        #    - Get prices for that date (use prices.filter())
        #    - Convert to dict for rebalancer: {ticker: close}
        #    - Decide if should rebalance (check frequency)
        #    - If rebalancing: calculate_trades() and execute them
        #    - Record portfolio state
        # 5. Build equity_curve and trades DataFrames from recorded data
        # 6. Return BacktestResult
        current_portfolio = Portfolio(initial_cash=config.initial_cash)
        current_rebalancer = Rebalancer()
        
        #data
        list_of_dates = pl.date_range(config.start_date,config.end_date,"1d",eager=True).to_list()
        last_rebalance_date = None
        equity_records = []
        trade_records = []
        for date in list_of_dates:
            daily_prices = prices.filter(pl.col("date") == date)
            prices_dict = {
                row["ticker"]: row["close"] for row in daily_prices.iter_rows(named=True)
            }
            rebalancing = self._should_rebalance(date,last_rebalance_date,config.rebalance_frequency)
            if rebalancing:
                rebalancing_trades = current_rebalancer.calculate_trades(current_portfolio=current_portfolio,
                                            target_weights=target_weights,
                                            prices=prices_dict,trade_date=date)
                for trade in rebalancing_trades:
                    if trade.side == "sell":
                        current_portfolio.sell(trade.ticker,trade.shares,
                                               trade.price,trade.date)
                    elif trade.side == "buy":
                        current_portfolio.buy(trade.ticker,trade.shares,
                                               trade.price,trade.date)
                    trade_records.append({
                        "date": trade.date,
                        "ticker": trade.ticker,
                        "shares": trade.shares,
                        "price": trade.price,
                        "side": trade.side
                    })
                last_rebalance_date = date
            total_value = current_portfolio.get_total_value(prices_dict)
            positions_value = current_portfolio.get_holdings_value(prices_dict)
            positions_value_sum = sum(positions_value.values())
            
            equity_records.append({
                "date":date,
                "portfolio_value":total_value,
                "cash":current_portfolio.cash,
                "positions_value":positions_value_sum
            })
            
        equity_curve = pl.DataFrame(equity_records)

        if trade_records:
            trades_df = pl.DataFrame(trade_records)
        else:
            # Empty DataFrame with correct schema
            trades_df = pl.DataFrame({
                "date": [],
                "ticker": [],
                "shares": [],
                "price": [],
                "side": []
            })

        return BacktestResult(equity_curve=equity_curve, trades=trades_df)

    def _should_rebalance(
        self,
        current_date: date,
        last_rebalance_date: date | None,
        frequency: str
    ) -> bool:
        """
        Check if should rebalance on this date.

        Parameters
        ----------
        current_date : date
            Today's date
        last_rebalance_date : date | None
            Last time we rebalanced (None if never)
        frequency : str
            "daily", "weekly", "monthly", or "never"

        Returns
        -------
        bool
            True if should rebalance today

        Examples
        --------
        - "daily": Always True
        - "never": Always False (except first day)
        - "weekly": True if 7+ days since last rebalance
        - "monthly": True if different month than last rebalance
        """
        # TODO: Implement this helper method
        # For now, you can start simple:
        # - "daily" → return True
        # - "never" → return True only if last_rebalance_date is None
        # - "weekly" and "monthly" → implement later if needed
        if frequency == "never":
            #unless sfirst day
            if last_rebalance_date == None:
                return True
        elif frequency == "daily":
            return True
        elif frequency == "weekly":
            if (current_date - last_rebalance_date).days >= 7:
                return True
        elif frequency == "monthly":
            if last_rebalance_date is None:
                return True
            return (last_rebalance_date.month != current_date.month or
                    last_rebalance_date.year != current_date.year)
        return False
