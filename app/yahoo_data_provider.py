"""
Yahoo Finance Data Provider - Replacement for TwelveData
Free, unlimited, real market data
"""

import logging
import asyncio
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

logger = logging.getLogger(__name__)


class YahooDataProvider:
    """Yahoo Finance data provider - Free and unlimited"""
    
    def __init__(self):
        logger.info("✅ YahooDataProvider initialized (Free, no API key needed!)")
    
    # Forex pair mapping: Our format → Yahoo format
    FOREX_MAP = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "USD/CHF": "USDCHF=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X",
        "NZD/USD": "NZDUSD=X",
        "EUR/GBP": "EURGBP=X",
        "EUR/JPY": "EURJPY=X",
        "GBP/JPY": "GBPJPY=X",
        "AUD/JPY": "AUDJPY=X",
        "EUR/CHF": "EURCHF=X",
        "GBP/CHF": "GBPCHF=X",
        "AUD/NZD": "AUDNZD=X",
        "EUR/AUD": "EURAUD=X",
        "EUR/CAD": "EURCAD=X",
        "GBP/AUD": "GBPAUD=X",
        "GBP/CAD": "GBPCAD=X",
        "AUD/CAD": "AUDCAD=X",
        "NZD/JPY": "NZDJPY=X",
        "CAD/JPY": "CADJPY=X",
        "CHF/JPY": "CHFJPY=X",
        "EUR/NZD": "EURNZD=X",
        "GBP/NZD": "GBPNZD=X",
        "AUD/CHF": "AUDCHF=X"
    }
    
    async def fetch_candles(
        self,
        pair: str,
        timeframe: str,
        n: int = 200
    ) -> Optional[pd.DataFrame]:
        """
        Fetch candles from Yahoo Finance
        
        Args:
            pair: Trading pair (e.g., "EUR/USD")
            timeframe: Timeframe (e.g., "1min", "5min", "1h")
            n: Number of candles to fetch
        
        Returns:
            DataFrame with columns: datetime, open, high, low, close, volume
        """
        try:
            # Convert pair to Yahoo format
            yahoo_symbol = self.FOREX_MAP.get(pair)
            if not yahoo_symbol:
                logger.warning(f"⚠️ Pair {pair} not supported by Yahoo Finance")
                return None
            
            # Convert timeframe to Yahoo interval
            interval_map = {
                "1min": "1m",
                "5min": "5m",
                "15min": "15m",
                "1h": "1h",
                "4h": "1h"  # Yahoo doesn't have 4h, use 1h
            }
            interval = interval_map.get(timeframe, "5m")
            
            # Calculate period based on n candles
            if interval == "1m":
                period = f"{min(n, 7)}d"  # Max 7 days for 1m
            elif interval == "5m":
                period = f"{min(n // 12, 60)}d"  # ~12 candles/hour
            elif interval == "15m":
                period = f"{min(n // 4, 60)}d"  # ~4 candles/hour
            else:  # 1h
                period = f"{min(n // 24, 730)}d"  # ~24 candles/day
            
            logger.info(f"🔍 Fetching {pair} ({yahoo_symbol}) on {interval}, period: {period}")
            
            # Fetch data (run in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: yf.download(
                    yahoo_symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=False
                )
            )
            
            if df is None or len(df) == 0:
                logger.warning(f"⚠️ No data returned for {pair}")
                return None
            
            # Flatten multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Reset index to get datetime as column
            df = df.reset_index()
            
            # Rename columns to match our format
            column_map = {
                'Datetime': 'datetime',
                'Date': 'datetime',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }
            df = df.rename(columns=column_map)
            
            # Ensure we have required columns
            required_cols = ['datetime', 'open', 'high', 'low', 'close']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"❌ Missing required columns for {pair}")
                return None
            
            # Add volume if missing
            if 'volume' not in df.columns:
                df['volume'] = 0
            
            # Convert types
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
            
            # Drop NaN rows
            df = df.dropna(subset=['open', 'high', 'low', 'close'])
            
            # Sort by datetime
            df = df.sort_values('datetime').reset_index(drop=True)
            
            # Take last n candles
            if len(df) > n:
                df = df.tail(n).reset_index(drop=True)
            
            logger.info(f"✅ Fetched {len(df)} candles for {pair} (requested: {n})")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching {pair}: {e}")
            return None
    
    async def fetch_multiple(
        self,
        pairs: list,
        timeframe: str,
        n: int = 200
    ) -> dict:
        """
        Fetch candles for multiple pairs in parallel
        
        Args:
            pairs: List of trading pairs
            timeframe: Timeframe
            n: Number of candles to fetch
        
        Returns:
            Dict mapping pair to DataFrame
        """
        logger.info(f"🔍 Fetching {len(pairs)} pairs on {timeframe}...")
        
        tasks = [self.fetch_candles(pair, timeframe, n) for pair in pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dict
        data_dict = {}
        for pair, result in zip(pairs, results):
            if isinstance(result, pd.DataFrame) and len(result) > 0:
                data_dict[pair] = result
            else:
                logger.warning(f"⚠️ Skipping {pair} (no data or error)")
        
        logger.info(f"✅ Got data for {len(data_dict)}/{len(pairs)} pairs")
        return data_dict
