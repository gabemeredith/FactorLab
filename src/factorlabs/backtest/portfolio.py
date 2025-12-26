"""
Portfolio class for tracking positions and cash.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Position:
    """Represents a position in a single security."""
    ticker: str
    shares: float
    entry_price: float
    entry_date: date


class Portfolio:
    """
    Tracks cash and positions over time.
    """
    
    def __init__(self, initial_cash: float = 100000.0):
        self.cash = initial_cash
        self.positions: dict[str, Position] = {}
    
    def get_total_value(self, prices: dict[str, float] = None) -> float:
        """
        Calculate total portfolio value.
        
        Parameters
        ----------
        prices : dict[str, float], optional
            Current prices for each ticker. If None, assumes only cash.
        
        Returns
        -------
        float
            Total value = cash + sum(position values)
        """
        if prices is None:
            # No positions valued yet, return just cash
            return self.cash
        
        positions_value = sum(
            pos.shares * prices.get(pos.ticker, 0.0)
            for pos in self.positions.values()
        )
        
        return self.cash + positions_value
    
    def buy(self, ticker: str, shares: float, price: float, date: date) -> None:
        """
        Execute a buy order.
        
        Parameters
        ----------
        ticker : str
            Stock ticker symbol
        shares : float
            Number of shares to buy
        price : float
            Price per share
        date : date
            Trade date
            
        Raises
        ------
        ValueError
            If insufficient cash
        """
        cost = shares * price
        
        if cost > self.cash:
            raise ValueError(
                f"Insufficient cash: need ${cost:,.2f}, have ${self.cash:,.2f}"
            )
        
        # Deduct cash
        self.cash -= cost
        
        # Add or update position
        if ticker in self.positions:
            # Already have position - update it (average cost basis)
            existing = self.positions[ticker]
            total_shares = existing.shares + shares
            avg_price = (
                (existing.shares * existing.entry_price + shares * price)
                / total_shares
            )
            self.positions[ticker] = Position(
                ticker=ticker,
                shares=total_shares,
                entry_price=avg_price,
                entry_date=existing.entry_date  # Keep original date
            )
        else:
            # New position
            self.positions[ticker] = Position(
                ticker=ticker,
                shares=shares,
                entry_price=price,
                entry_date=date
            )
        
    def sell(self,ticker: str, shares: float,price: float, date: date) -> None:
        """
        executes a sell order

         Parameters
        ----------
        ticker : str
            Stock ticker symbol
        shares : float
            Number of shares to buy
        price : float
            Price per share
        date : date
            Trade date
            
        """
        if shares <= 0:
            raise ValueError("Shares must be positive")
        
        if ticker not in self.positions:
            raise ValueError(f"No position in {ticker}")
        
        if shares > self.positions[ticker].shares:
            raise ValueError(
                f"Insufficient shares: trying to sell {shares},"
                f"only own {self.positions[ticker].shares}"
            )
            
        proceeds = shares * price 
        self.cash += proceeds
        
        if shares == self.positions[ticker].shares:
            del self.positions[ticker]
        else:
            self.positions[ticker].shares -= shares
            