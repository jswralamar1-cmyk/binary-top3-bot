"""
Data Provider - Phase C
Fetches candle data from TwelveData API
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
import pandas as pd

from app.config import (
    TWELVEDATA_API_KEY,
    TWELVEDATA_API_URL,
    API_TIMEOUT,
    API_RETRY,
    API_SEMAPHORE
)

logger = logging.getLogger(__name__)


class DataProvider:
    """TwelveData API provider"""
    
    def __init__(self):
        self.api_key = TWELVEDATA_API_KEY
        if not self.api_key:
            raise RuntimeError("❌ Missing TWELVEDATA_API_KEY")
        
        self.semaphore = asyncio.Semaphore(API_SEMAPHORE)
        logger.info(f"✅ DataProvider initialized (semaphore: {API_SEMAPHORE})")
    
    async def fetch_candles(
        self,
        pair: str,
        timeframe: str,
        n: int = 5000
    ) -> Optional[pd.DataFrame]:
        """
        Fetch candles from TwelveData API
        
        Args:
            pair: Trading pair (e.g., "EUR/USD")
            timeframe: Timeframe (e.g., "1min", "5min", "1h", "4h")
            n: Number of candles to fetch
        
        Returns:
            DataFrame with columns: time, open, high, low, close, volume
            or None if error
        """
        async with self.semaphore:
            for attempt in range(API_RETRY + 1):
                try:
                    # Keep slash for Forex pairs (TwelveData requires EUR/USD format)
                    symbol = pair
                    
                    # Convert timeframe format: 1min -> 1m, 5min -> 5m, etc.
                    interval_map = {
                        "1min": "1min",
                        "5min": "5min",
                        "15min": "15min",
                        "1h": "1h",
                        "4h": "4h"
                    }
                    interval = interval_map.get(timeframe, timeframe)
                    
                    params = {
                        "symbol": symbol,
                        "interval": interval,
                        "outputsize": str(n),
                        "apikey": self.api_key,
                        "format": "JSON",
                    }
                    
                    logger.debug(f"🔍 Fetching {symbol} ({pair}) on {interval}...")
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            TWELVEDATA_API_URL,
                            params=params,
                            timeout=API_TIMEOUT
                        )
                        response.raise_for_status()
                        data = response.json()
                    
                    # Debug: log response
                    logger.info(f"📦 API response keys: {list(data.keys())}")
                    if "values" in data:
                        logger.info(f"📊 Number of values returned: {len(data['values'])}")
                    
                    # Check for API errors
                    if "status" in data and data["status"] == "error":
                        logger.error(f"❌ API error for {pair} on {timeframe}: {data.get('message')}")
                        logger.error(f"📦 Full response: {data}")
                        return None
                    
                    # Check for code/message error format
                    if "code" in data and data.get("code") != 200:
                        logger.error(f"❌ API error for {pair}: {data.get('message', 'Unknown error')}")
                        logger.error(f"📦 Full response: {data}")
                        return None
                    
                    values = data.get("values")
                    if not values:
                        logger.warning(f"⚠️ No data for {pair} on {timeframe}")
                        return None
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(values)
                    
                    # TwelveData returns newest first, reverse to get oldest first
                    df = df.iloc[::-1].reset_index(drop=True)
                    
                    # Convert types
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    df["open"] = pd.to_numeric(df["open"], errors="coerce")
                    df["high"] = pd.to_numeric(df["high"], errors="coerce")
                    df["low"] = pd.to_numeric(df["low"], errors="coerce")
                    df["close"] = pd.to_numeric(df["close"], errors="coerce")
                    df["volume"] = pd.to_numeric(df.get("volume", 0), errors="coerce")
                    
                    # Drop NaN rows
                    df = df.dropna(subset=["open", "high", "low", "close"])
                    
                    if len(df) < 50:
                        logger.warning(f"⚠️ Insufficient data for {pair} on {timeframe}: {len(df)} candles (requested: {n})")
                        logger.warning(f"📦 First few rows: {df.head(3).to_dict()}")
                        # Don't return None, use what we have for debugging
                        # return None
                    
                    logger.info(f"✅ Fetched {len(df)} candles for {pair} on {timeframe} (requested: {n})")
                    return df
                
                except httpx.TimeoutException:
                    logger.warning(f"⏱️ Timeout for {pair} on {timeframe} (attempt {attempt + 1}/{API_RETRY + 1})")
                    if attempt < API_RETRY:
                        await asyncio.sleep(1)
                    else:
                        logger.error(f"❌ Max retries reached for {pair} on {timeframe}")
                        return None
                
                except Exception as e:
                    logger.error(f"❌ Error fetching {pair} on {timeframe}: {e}")
                    if attempt < API_RETRY:
                        await asyncio.sleep(1)
                    else:
                        return None
        
        return None
    
    async def fetch_multiple(
        self,
        pairs: List[str],
        timeframe: str,
        n: int = 5000
    ) -> Dict[str, pd.DataFrame]:
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
            if isinstance(result, pd.DataFrame):
                data_dict[pair] = result
            else:
                logger.warning(f"⚠️ Skipping {pair} (no data or error)")
        
        logger.info(f"✅ Got data for {len(data_dict)}/{len(pairs)} pairs")
        return data_dict
