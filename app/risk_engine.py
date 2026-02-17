"""
Risk Engine - Phase I
Checks for news events and high spread
Adds warnings to signals
"""

import logging
from typing import List
from datetime import datetime, timedelta

from app.config import NEWS_WARNING_WINDOW, MAX_SPREAD_MULTIPLIER
from app.models import Signal

logger = logging.getLogger(__name__)


class RiskEngine:
    """Risk management engine"""
    
    def __init__(self):
        # Simplified news calendar (high-impact events)
        # In production, fetch from API like ForexFactory or Investing.com
        self.news_calendar = []
        logger.info("✅ RiskEngine initialized")
    
    def check_news_risk(self, signal: Signal) -> List[str]:
        """
        Check if signal is near high-impact news
        
        Args:
            signal: Signal to check
        
        Returns:
            List of warnings
        """
        warnings = []
        
        # Extract currency codes from pair
        base = signal.pair[:3]
        quote = signal.pair[4:7]
        
        # Get current time
        now = datetime.utcnow()
        
        # Check news calendar
        for news in self.news_calendar:
            news_time = news["time"]
            news_currency = news["currency"]
            news_impact = news["impact"]
            
            # Check if news affects this pair
            if news_currency not in [base, quote]:
                continue
            
            # Check if within warning window
            time_diff = abs((news_time - now).total_seconds() / 60)
            
            if time_diff <= NEWS_WARNING_WINDOW:
                warnings.append(f"⚠️ أخبار {news_impact} لـ {news_currency} خلال {int(time_diff)} دقيقة")
        
        return warnings
    
    def check_spread_risk(self, signal: Signal) -> List[str]:
        """
        Check if spread is too high
        
        Args:
            signal: Signal to check
        
        Returns:
            List of warnings
        """
        warnings = []
        
        # In production, fetch real-time spread from broker API
        # For now, estimate spread from ATR
        features = signal.features
        atr = features["atr"]
        
        # Estimate spread as % of ATR
        # If ATR is very low, spread becomes significant
        if atr < 0.0005:  # Very low volatility
            warnings.append("⚠️ تقلب منخفض جداً - السبريد قد يكون مرتفع نسبياً")
        
        # Check if market is range-bound (higher spread impact)
        if signal.market_state == "range":
            warnings.append("⚠️ سوق عرضي (Range) - احذر من False Breakouts")
        
        return warnings
    
    def check_time_risk(self, signal: Signal) -> List[str]:
        """
        Check if trading time is risky
        
        Args:
            signal: Signal to check
        
        Returns:
            List of warnings
        """
        warnings = []
        
        # Get current time (UTC)
        now = datetime.utcnow()
        hour = now.hour
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday
        
        # Asian session (low liquidity for EUR/GBP/USD)
        if 0 <= hour < 6:
            if any(curr in signal.pair for curr in ["EUR", "GBP", "USD"]):
                warnings.append("⚠️ جلسة آسيا - سيولة منخفضة لأزواج EUR/GBP/USD")
        
        # Friday after 16:00 UTC (weekend risk)
        if day_of_week == 4 and hour >= 16:
            warnings.append("⚠️ نهاية الأسبوع - احذر من الفجوات (Gaps)")
        
        # Sunday evening (market opening, high volatility)
        if day_of_week == 6 and 21 <= hour <= 23:
            warnings.append("⚠️ افتتاح السوق - تقلبات عالية محتملة")
        
        return warnings
    
    def assess_risk_level(self, signal: Signal) -> str:
        """
        Assess overall risk level
        
        Args:
            signal: Signal with warnings
        
        Returns:
            "منخفض", "متوسط", or "عالي"
        """
        warning_count = len(signal.warnings)
        
        # Check for critical warnings
        critical_keywords = ["أخبار عالية", "أخبار HIGH", "نهاية الأسبوع"]
        has_critical = any(kw in w for w in signal.warnings for kw in critical_keywords)
        
        if has_critical or warning_count >= 3:
            return "عالي"
        elif warning_count >= 1:
            return "متوسط"
        else:
            return "منخفض"
    
    def add_risk_warnings(self, signals: List[Signal]) -> List[Signal]:
        """
        Add risk warnings to signals
        
        Args:
            signals: List of signals
        
        Returns:
            Signals with warnings added
        """
        for signal in signals:
            warnings = []
            
            # Check news risk
            warnings.extend(self.check_news_risk(signal))
            
            # Check spread risk
            warnings.extend(self.check_spread_risk(signal))
            
            # Check time risk
            warnings.extend(self.check_time_risk(signal))
            
            # Add warnings to signal
            signal.warnings = warnings
            
            # Assess risk level
            signal.risk_level = self.assess_risk_level(signal)
            
            if warnings:
                logger.debug(f"⚠️ {signal.pair} has {len(warnings)} warnings (risk: {signal.risk_level})")
        
        logger.info(f"✅ Added risk warnings to {len(signals)} signals")
        return signals
