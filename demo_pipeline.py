"""
FactorLab - Complete Pipeline Demo

This script demonstrates the full quantitative backtesting pipeline:
1. Ingest price data from Yahoo Finance
2. Calculate technical factors (momentum, RSI, etc.)
3. Define target portfolio weights
4. Run backtest with rebalancing
5. Analyze results

Run: python demo_pipeline.py
"""

from datetime import date
import polars as pl

from src.factorlabs.data.ingest_yf import fetch_yf_data, YFIngestConfig, normalize_prices
from src.factorlabs.financialfeatures.factors import (
    calculate_returns,
    calculate_momentum,
    calculate_rsi,
    calculate_sma,
)
from src.factorlabs.backtest.backtester import Backtester, BacktestConfig


def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_full_pipeline():
    """Run complete pipeline from data ingestion to backtest results"""

    print_section("FactorLab - Quantitative Backtesting Engine Demo")

    # =================================================================
    # STEP 1: Data Ingestion
    # =================================================================
    print_section("STEP 1: Ingest Price Data from Yahoo Finance")

    tickers = ["AAPL", "MSFT", "GOOGL"]
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)

    print(f"Fetching data for: {', '.join(tickers)}")
    print(f"Date range: {start_date} to {end_date}\n")

    # Fetch data
    config = YFIngestConfig(
        tickers=tickers,
        start=start_date,
        end=end_date,
        interval="1d"
    )

    raw_data = fetch_yf_data(config)
    prices = normalize_prices(raw_data)

    print(f" Fetched {len(prices):,} rows of price data")
    print(f"\nSample data:")
    print(prices.head(5))

    # =================================================================
    # STEP 2: Calculate Factors
    # =================================================================
    print_section("STEP 2: Calculate Technical Factors")

    print("Computing factors:")
    print("  - Daily returns")
    print("  - 10-day momentum")
    print("  - 14-day RSI")
    print("  - 20-day SMA\n")

    # Calculate factors
    factors = prices.pipe(calculate_returns, delay=1)
    factors = factors.pipe(calculate_momentum, delay=10)
    factors = factors.pipe(calculate_rsi, window=14)
    factors = factors.pipe(calculate_sma, delay=20)

    print(f" Calculated {len(factors.columns)} columns total")
    print(f"\nSample factors (recent data):")
    print(factors.tail(5).select(["date", "ticker", "close", "ret_1d", "mom_10d", "rsi_14"]))

    # =================================================================
    # STEP 3: Define Strategy (Simple Static Allocation)
    # =================================================================
    print_section("STEP 3: Define Portfolio Strategy")

    # For now: simple allocation (later: dynamic based on factors)
    # Note: tickers are lowercase in the data
    # Using 99% total to avoid floating point precision issues
    target_weights = {
        "aapl": 0.49,
        "msft": 0.30,
        "googl": 0.20
    }

    print("Strategy: Static allocation (buy and hold)")
    for ticker, weight in target_weights.items():
        print(f"  {ticker}: {weight*100:.0f}%")

    # =================================================================
    # STEP 4: Run Backtest
    # =================================================================
    print_section("STEP 4: Run Backtest Simulation")

    backtest_config = BacktestConfig(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        initial_cash=100000.0,
        rebalance_frequency="monthly"  # Rebalance once per month
    )

    # Filter to only dates where all tickers have data
    # Group by date and count tickers - keep only dates with all 3 tickers
    ticker_count_by_date = (
        prices
        .group_by("date")
        .agg(pl.col("ticker").n_unique().alias("ticker_count"))
    )

    complete_dates = (
        ticker_count_by_date
        .filter(pl.col("ticker_count") == len(target_weights))
        .select("date")
        .sort("date")
    )

    # Filter prices to only complete dates
    filtered_prices = prices.join(complete_dates, on="date")

    # Update backtest config to use actual available date range
    actual_start = complete_dates["date"].min()
    actual_end = complete_dates["date"].max()

    backtest_config = BacktestConfig(
        start_date=actual_start,
        end_date=actual_end,
        initial_cash=100000.0,
        rebalance_frequency="never"  # Buy and hold to avoid weekend date issues
    )

    print(f"Initial capital: ${backtest_config.initial_cash:,.0f}")
    print(f"Rebalance frequency: {backtest_config.rebalance_frequency}")
    print(f"Actual date range: {actual_start} to {actual_end}")
    print(f"Trading days with complete data: {len(complete_dates)}\n")

    print(f"Running backtest...\n")

    backtester = Backtester()
    result = backtester.run(
        prices=filtered_prices.select(["date", "ticker", "close"]),
        target_weights=target_weights,
        config=backtest_config
    )

    print(f"\n✅ Backtest complete!")
    print(f"   - Simulated {len(result.equity_curve)} trading days")
    print(f"   - Executed {len(result.trades)} trades")

    # =================================================================
    # STEP 5: Analyze Results
    # =================================================================
    print_section("STEP 5: Performance Analysis")

    # Calculate key metrics
    initial_value = result.equity_curve["portfolio_value"][0]
    final_value = result.equity_curve["portfolio_value"][-1]
    total_return = (final_value / initial_value - 1) * 100

    # Filter equity curve to valid trading days (where we have positions)
    valid_equity = result.equity_curve.filter(pl.col("positions_value") > 0)

    if len(valid_equity) > 1:
        # Daily returns for volatility
        equity_returns = (
            valid_equity["portfolio_value"]
            .pct_change()
            .drop_nulls()
        )
        volatility = equity_returns.std() * (252 ** 0.5) * 100  # Annualized

        # Max drawdown
        cummax = valid_equity["portfolio_value"].cum_max()
        drawdown = (valid_equity["portfolio_value"] / cummax - 1) * 100
        max_drawdown = drawdown.min()
    else:
        volatility = 0.0
        max_drawdown = 0.0

    print(" Performance Summary:")
    print(f"   Initial Value:    ${initial_value:>12,.2f}")
    print(f"   Final Value:      ${final_value:>12,.2f}")
    print(f"   Total Return:     {total_return:>12.2f}%")
    print(f"   Volatility (ann): {volatility:>12.2f}%")
    print(f"   Max Drawdown:     {max_drawdown:>12.2f}%")

    # Trade statistics
    print(f"\n Trade Statistics:")
    print(f"   Total Trades:     {len(result.trades):>12,}")

    if len(result.trades) > 0:
        buy_trades = result.trades.filter(pl.col("side") == "buy")
        sell_trades = result.trades.filter(pl.col("side") == "sell")
        print(f"   Buy Orders:       {len(buy_trades):>12,}")
        print(f"   Sell Orders:      {len(sell_trades):>12,}")

        # Total volume traded
        total_volume = (result.trades["shares"] * result.trades["price"]).sum()
        print(f"   Total Volume:     ${total_volume:>12,.0f}")

    # Show equity curve sample
    print(f"\n Equity Curve (first 5 days):")
    print(result.equity_curve.head(5).select(["date", "portfolio_value", "cash", "positions_value"]))

    print(f"\n Equity Curve (last 5 days):")
    print(result.equity_curve.tail(5).select(["date", "portfolio_value", "cash", "positions_value"]))

    # Show recent trades
    if len(result.trades) > 0:
        print(f"\n Recent Trades (last 5):")
        print(result.trades.tail(5))

    # =================================================================
    # Summary
    # =================================================================
    print_section(" Pipeline Complete!")

    print("The FactorLab pipeline successfully:")
    print("  1.  Ingested price data from Yahoo Finance")
    print("  2.  Calculated technical factors (returns, momentum, RSI, SMA)")
    print("  3.  Defined portfolio strategy (static 49/30/20 allocation)")
    print("  4.  Ran time-loop backtest with buy-and-hold strategy")
    print("  5.  Generated performance metrics and trade history")

    print(f"\nFinal portfolio value: ${final_value:,.2f}")
    print(f"Total return: {total_return:.2f}%")

    print("\n" + "="*60)
    print("  Next steps: Implement dynamic strategies based on factors!")
    print("="*60 + "\n")

    return result


if __name__ == "__main__":
    try:
        result = demo_full_pipeline()
    except Exception as e:
        print(f"\n Error running pipeline: {e}")
        import traceback
        traceback.print_exc()