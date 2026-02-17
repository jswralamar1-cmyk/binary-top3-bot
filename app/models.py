"""
Data models for Binary Top3 Bot
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class UserSelection:
    """User's scan configuration"""
    mode: Optional[str] = None  # "sniper" or "momentum"
    expiry: Optional[int] = None  # 1 or 3 minutes
    timeframe: Optional[str] = None  # "1min", "5min", etc.
    
    def is_complete(self) -> bool:
        """Check if all selections are made"""
        return all([self.mode, self.expiry, self.timeframe])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "mode": self.mode,
            "expiry": self.expiry,
            "timeframe": self.timeframe
        }


@dataclass
class Signal:
    """Trading signal"""
    pair: str
    tf: str
    direction: str  # "CALL" or "PUT"
    score: float
    market_state: str  # "trend" or "range"
    reasons: List[str] = field(default_factory=list)
    features: Dict[str, Any] = field(default_factory=dict)
    
    # Confirmation
    confirmed_5m: bool = False
    
    # Entry plan
    trigger_price: Optional[float] = None
    current_price: Optional[float] = None
    distance_pips: Optional[float] = None
    validity_seconds: Optional[int] = None
    expiry_minutes: Optional[int] = None
    
    # Risk
    warnings: List[str] = field(default_factory=list)
    risk_level: str = "متوسط"
    
    # Chart
    chart_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pair": self.pair,
            "tf": self.tf,
            "direction": self.direction,
            "score": self.score,
            "market_state": self.market_state,
            "reasons": self.reasons,
            "features": self.features,
            "confirmed_5m": self.confirmed_5m,
            "trigger_price": self.trigger_price,
            "current_price": self.current_price,
            "distance_pips": self.distance_pips,
            "validity_seconds": self.validity_seconds,
            "expiry_minutes": self.expiry_minutes,
            "warnings": self.warnings,
            "risk_level": self.risk_level,
            "chart_path": self.chart_path
        }


@dataclass
class ScanResult:
    """Result of a market scan"""
    mode: str
    expiry: int
    timeframe: str
    signals: List[Signal] = field(default_factory=list)
    scan_time: Optional[str] = None
    total_pairs: int = 0
    filtered_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "mode": self.mode,
            "expiry": self.expiry,
            "timeframe": self.timeframe,
            "signals": [s.to_dict() for s in self.signals],
            "scan_time": self.scan_time,
            "total_pairs": self.total_pairs,
            "filtered_count": self.filtered_count
        }
