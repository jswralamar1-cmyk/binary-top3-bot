"""
Ranking Engine - Phase H
Ranks signals and returns Top 3
Implements Strategy Tiers (Strong/Valid/Aggressive)
"""

import logging
from typing import List

from app.config import TIER_STRONG, TIER_VALID, TIER_AGGRESSIVE, MAX_RESULTS
from app.models import Signal

logger = logging.getLogger(__name__)


class RankingEngine:
    """Signal ranking engine"""
    
    def __init__(self):
        logger.info("✅ RankingEngine initialized")
    
    def get_tier(self, score: float) -> tuple:
        """
        Get tier emoji and name for score
        
        Args:
            score: Signal score
        
        Returns:
            (emoji, tier_name)
        """
        if score >= TIER_STRONG:
            return ("🔥🔥🔥", "إعداد قوي جداً")
        elif score >= TIER_VALID:
            return ("🔥🔥", "إعداد صالح")
        elif score >= TIER_AGGRESSIVE:
            return ("🔥", "إعداد جريء")
        else:
            return ("⚠️", "ضعيف")
    
    def rank_signals(self, signals: List[Signal]) -> List[Signal]:
        """
        Rank signals by score and return Top 3
        
        Args:
            signals: List of signals
        
        Returns:
            Top 3 signals (or less if not enough)
        """
        if not signals:
            logger.info("⚠️ No signals to rank")
            return []
        
        # Sort by score (descending)
        sorted_signals = sorted(signals, key=lambda s: s.score, reverse=True)
        
        # Take top N
        top_signals = sorted_signals[:MAX_RESULTS]
        
        logger.info(f"✅ Ranked signals: Top {len(top_signals)} from {len(signals)}")
        
        # Log top signals
        for i, signal in enumerate(top_signals, 1):
            emoji, tier = self.get_tier(signal.score)
            logger.info(f"  #{i} {signal.pair} {signal.direction} {signal.score:.0f} {emoji} {tier}")
        
        return top_signals
    
    def filter_by_tier(self, signals: List[Signal], min_tier: str = "valid") -> List[Signal]:
        """
        Filter signals by minimum tier
        
        Args:
            signals: List of signals
            min_tier: "strong", "valid", or "aggressive"
        
        Returns:
            Filtered signals
        """
        if min_tier == "strong":
            min_score = TIER_STRONG
        elif min_tier == "valid":
            min_score = TIER_VALID
        elif min_tier == "aggressive":
            min_score = TIER_AGGRESSIVE
        else:
            min_score = 0
        
        filtered = [s for s in signals if s.score >= min_score]
        
        logger.info(f"✅ Filtered {len(filtered)}/{len(signals)} signals (min_tier={min_tier}, min_score={min_score})")
        
        return filtered
