from dataclasses import dataclass
from datetime import date
import datetime
from typing import Sequence
import yfinance as yf
import polars as pl
import time
import ast
@dataclass
class YFIngestConfig:
    tickers: Sequence[str]
    start: date
    end: date
    interval: str
    adjust: bool = True
    out_path: str = "data/yf_prices.parquet"

def fetch_yf_data(cfg: YFIngestConfig) -> pl.DataFrame:
    """
    Function to fetch yahoo finance data and put it into a polars dataframe
    
    Parameters:cfg(YFIngestConfig)
    Preconditions:cfg is a YFIngestConfig
    """
    assert isinstance(cfg,YFIngestConfig), "cfg isnt a YFIngestConfig"
    data = yf.download(tickers=cfg.tickers,start=cfg.start,
                       end=cfg.end,interval=cfg.interval,
                       auto_adjust=cfg.adjust,
                       progress=False,)
    if data.empty:
        raise ValueError("No data returned from yfinance for given config")
    
    data = data.reset_index()

    df = pl.from_pandas(data)
    return df

def normalize_prices(df: pl.DataFrame) -> pl.DataFrame:
    # standardize columns, dtypes, timezone, multiindex -> tidy, etc.
    """
    Normalize a raw price DataFrame into the standard FactorLabs price schema.

    This function takes the raw output returned by the data source (typically 
    yfinance) and performs the following transformations:

    1. Column normalization:
       - Ensures all column names are lower_snake_case.
       - Renames vendor-specific fields (e.g., 'Adj Close' -> 'adj_close').
       - Ensures a consistent set of price fields when available:
         ['open', 'high', 'low', 'close', 'adj_close', 'volume'].

    2. Index & date normalization:
       - Ensures there is a 'date' column of type Date.
       - Removes timezone information and normalizes to UTC if present.
       - Sorts the DataFrame by ['ticker', 'date'] when a ticker column exists.

    3. Multi-ticker handling:
       - If the raw DataFrame is in yfinance's wide/multi-index format, 
         it is converted to a tidy long-form schema with columns:
         ['ticker', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume'].

    4. Data-quality fixes:
       - Drops rows with entirely null OHLCV values.
       - Enforces non-negative prices and integer volume where applicable.
       - Ensures no duplicate (ticker, date) combinations.

    Returns
    -------
    pl.DataFrame
        A clean, canonical, long-form price dataset suitable for all downstream 
        FactorLabs pipeline stages (feature engineering, sleeves, backtesting).

    Notes
    -----
    This function should contain **no vendor-specific API calls**. Its only job 
    is to take raw price data and standardize its structure and schema.
    """
    #step 1 -> normalize the column names
    df = normalize_column_names(df)
    df = normalize_date_columns(df)
    #step 2 -> ensure there is a date column w/ datatypes of date
    
# ---------------------------------------------HELPER FUNCTIONS FOR NORMALIZE_PRICES----------------------------------------------
def normalize_date_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    Takes in a polars dataframe, checks if it has a dates column.
    then checks if the dates column is of type date, and if removes timezone information
    normalizing to UTC if present. Sorts the dataeframe by ['ticker','date'] when a ticker column exists.

    Examples: 
    

    Returns:
        pl.DataFrame: _description_
    """
    dtype_map = {name: dtype for name, dtype in zip(df.columns, df.dtypes)}
    print(dtype_map["date"]) # possible outputs for datetime objects are DateTime
    type_date  = dtype_map["date"]
    if isinstance(type_date,pl.Datetime):
        #expected this is chill but lets make sure its normalized 
        if type_date.time_zone is not None:
            df.columns["date"].convert_time_zone("UTC")
        else;
    if isinstance(type_date,str):
        #convert from str to date
        try:
            df.with_columns(dt = pl.col('date')
                            .str.to_datetime().cast(
                                pl.Date
                            ))
        except Exception as e:
            print(e)
            return None
    if 
    return 0
def normalize_column_names(df: pl.DataFrame) -> pl.DataFrame:
    """
    Flatten yfinance-style MultiIndex columns into lower_snake_case strings.

    Examples
    --------
    ('Date', '')        -> 'date'
    ('Close', 'AAPL')   -> 'close_aapl'
    ('Volume', 'MSFT')  -> 'volume_msft'
    """
    rename_map = {}

    for col in df.columns:
        name = str(col)

        # Case 1: looks like "('close', 'aapl')" -> parse as a tuple
        if name.startswith("(") and name.endswith(")"):
            try:
                level1, level2 = ast.literal_eval(name)  # ('close', 'aapl')
            except (SyntaxError, ValueError):
                # fallback: just lowercase the raw string
                new_name = name.lower()
            else:
                level1 = (level1 or "").strip().lower()
                level2 = (level2 or "").strip().lower()

                if level2 == "":
                    # e.g. ('date', '') -> 'date'
                    new_name = level1
                else:
                    # e.g. ('close', 'aapl') -> 'close_aapl'
                    new_name = f"{level1}_{level2}"
        else:
            # Case 2: already a simple string column
            new_name = name.lower()

        rename_map[col] = new_name

    return df.rename(rename_map)

def write_prices(df: pl.DataFrame, cfg: YFIngestConfig) -> None:
    # write to DuckDB or Parquet
    ...

def run_ingest(cfg: YFIngestConfig) -> None:
    raw = fetch_yf_data(cfg)
    normalized = normalize_prices(raw)
    write_prices(normalized, cfg)

def main():
    # parse argparse / typer, build YFIngestConfig, call run_ingest
    ...

if __name__ == "__main__":
    cfg = YFIngestConfig(
        tickers=["AAPL", "MSFT"],
        start=date(2024, 1, 1),
        end=date(2024, 1, 10),
        interval="1d",
    )
    time1 = time.time()
    df = fetch_yf_data(cfg)
    time2 = time.time()
    print(f"TIME TAKEN TO COMPUTE: {time2 - time1}")
    df = normalize_prices(df)
    print(df.head())
    print(df.columns)