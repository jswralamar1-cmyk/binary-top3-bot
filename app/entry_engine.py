"""
Entry Engine - Phase G
Calculates entry trigger price and validity window
"""

import logging
from typing import List
from datetime import datetime, timedelta

from app.config import TRIGGER_BUFFER_MULTIPLIER, VALIDITY_1M, VALIDITY_3M
from app.models import Signal

logger = logging.getLogger(__name__)


class EntryEngine:
    """Entry trigger calculator"""
    
    def __init__(self):
        logger.info("✅ EntryEngine initialized")
    
    def calculate_entry_trigger(self, signal: Signal, expiry: int) -> Signal:
        """
        Calculate entry trigger price and validity window
        
        Args:
            signal: Signal object
            expiry: Expiry in minutes (1 or 3)
        
        Returns:
            Signal with entry plan filled
        """
        features = signal.features
        
        # Get current price
        current_price = features["close"]
        
        # Get ATR
        atr = features["atr"]
        
        # Calculate trigger buffer (15% of ATR)
        trigger_buffer = atr * TRIGGER_BUFFER_MULTIPLIER
        
        # Calculate trigger price
        if signal.direction == "CALL":
            # For CALL, trigger = last high + buffer
            trigger_price = features["high"] + trigger_buffer
        else:
            # For PUT, trigger = last low - buffer
            trigger_price = features["low"] - trigger_buffer
        
        # Calculate distance in pips (assuming 4-digit pairs, adjust for JPY)
        if "JPY" in signal.pair:
            # JPY pairs: 1 pip = 0.01
            distance_pips = abs(trigger_price - current_price) * 100
        else:
            # Other pairs: 1 pip = 0.0001
            distance_pips = abs(trigger_price - current_price) * 10000
        
        # Validity window
        if expiry == 1:
            validity_seconds = VALIDITY_1M
        else:
            validity_seconds = VALIDITY_3M
        
        # Fill signal
        signal.trigger_price = trigger_price
        signal.current_price = current_price
        signal.distance_pips = distance_pips
        signal.validity_seconds = validity_seconds
        signal.expiry_minutes = expiry
        
        logger.debug(f"✅ Entry plan for {signal.pair}: trigger={trigger_price:.5f}, current={current_price:.5f}, distance={distance_pips:.1f} pips")
        
        return signal
    
    def calculate_entry_plans(self, signals: List[Signal], expiry: int) -> List[Signal]:
        """
        Calculate entry plans for multiple signals
        
        Args:
            signals: List of signals
            expiry: Expiry in minutes
        
        Returns:
            List of signals with entry plans
        """
        for signal in signals:
            self.calculate_entry_trigger(signal, expiry)
        
        logger.info(f"✅ Calculated entry plans for {len(signals)} signals")
        return signals
