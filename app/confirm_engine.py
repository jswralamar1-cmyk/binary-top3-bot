"""
Confirm Engine - Phase F
Optional 5m confirmation for signals
"""

import logging
import pandas as pd
from typing import List, Optional

from app.models import Signal
from app.data_provider import DataProvider
from app.indicators import calculate_all_indicators, get_last_candle_features

logger = logging.getLogger(__name__)


class ConfirmEngine:
    """5m confirmation engine"""
    
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        logger.info("✅ ConfirmEngine initialized")
    
    async def confirm_signal(self, signal: Signal) -> bool:
        """
        Confirm signal on 5m timeframe
        
        Args:
            signal: Signal to confirm
        
        Returns:
            True if confirmed, False otherwise
        """
        try:
            # Fetch 5m data
            df_5m = await self.data_provider.fetch_candles(signal.pair, "5min", n=100)
            
            if df_5m is None or len(df_5m) < 50:
                logger.warning(f"⚠️ Insufficient 5m data for {signal.pair}")
                return False
            
            # Calculate indicators
            df_5m = calculate_all_indicators(df_5m)
            features_5m = get_last_candle_features(df_5m)
            
            # Check direction alignment
            if signal.direction == "CALL":
                # For CALL, 5m should show uptrend or at least EMA9 > EMA21
                if features_5m["trend"] == "uptrend":
                    logger.debug(f"✅ 5m confirms CALL for {signal.pair} (uptrend)")
                    return True
                elif features_5m["ema9"] > features_5m["ema21"] and features_5m["rsi"] > 50:
                    logger.debug(f"✅ 5m confirms CALL for {signal.pair} (EMA + RSI)")
                    return True
                else:
                    logger.debug(f"❌ 5m does not confirm CALL for {signal.pair}")
                    return False
            
            elif signal.direction == "PUT":
                # For PUT, 5m should show downtrend or at least EMA9 < EMA21
                if features_5m["trend"] == "downtrend":
                    logger.debug(f"✅ 5m confirms PUT for {signal.pair} (downtrend)")
                    return True
                elif features_5m["ema9"] < features_5m["ema21"] and features_5m["rsi"] < 50:
                    logger.debug(f"✅ 5m confirms PUT for {signal.pair} (EMA + RSI)")
                    return True
                else:
                    logger.debug(f"❌ 5m does not confirm PUT for {signal.pair}")
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"❌ Error confirming {signal.pair}: {e}")
            return False
    
    async def confirm_signals(self, signals: List[Signal]) -> List[Signal]:
        """
        Confirm multiple signals on 5m timeframe
        
        Args:
            signals: List of signals to confirm
        
        Returns:
            List of confirmed signals
        """
        confirmed = []
        
        for signal in signals:
            is_confirmed = await self.confirm_signal(signal)
            signal.confirmed_5m = is_confirmed
            
            if is_confirmed:
                confirmed.append(signal)
                logger.debug(f"✅ {signal.pair} confirmed on 5m")
            else:
                logger.debug(f"❌ {signal.pair} not confirmed on 5m")
        
        logger.info(f"✅ Confirmed {len(confirmed)}/{len(signals)} signals on 5m")
        return confirmed
