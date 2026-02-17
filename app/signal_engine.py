"""
Signal Engine - Phase E
Generates trading signals with scoring
Implements Sniper and Momentum logic
"""

import logging
import pandas as pd
from typing import List, Dict, Any, Optional

from app.config import MODE_SNIPER, MODE_MOMENTUM, TIER_STRONG, TIER_VALID, TIER_AGGRESSIVE
from app.indicators import calculate_all_indicators, get_last_candle_features
from app.models import Signal

logger = logging.getLogger(__name__)


class SignalEngine:
    """Signal generation engine"""
    
    def __init__(self):
        logger.info("✅ SignalEngine initialized")
    
    def analyze_pair(
        self,
        pair: str,
        df: pd.DataFrame,
        mode: str,
        timeframe: str
    ) -> Optional[Signal]:
        """
        Analyze a single pair and generate signal
        
        Args:
            pair: Trading pair
            df: DataFrame with OHLCV data
            mode: "sniper" or "momentum"
            timeframe: Timeframe
        
        Returns:
            Signal object or None if no signal
        """
        # Calculate indicators
        df = calculate_all_indicators(df)
        
        # Get last candle features
        features = get_last_candle_features(df)
        
        # Analyze based on mode
        if mode == MODE_SNIPER:
            return self._analyze_sniper(pair, df, features, timeframe)
        elif mode == MODE_MOMENTUM:
            return self._analyze_momentum(pair, df, features, timeframe)
        else:
            logger.error(f"❌ Unknown mode: {mode}")
            return None
    
    def _analyze_sniper(
        self,
        pair: str,
        df: pd.DataFrame,
        features: Dict[str, Any],
        timeframe: str
    ) -> Optional[Signal]:
        """
        Analyze for Sniper mode (1M)
        
        Requirements:
        - ATR spike (> 1.5× average)
        - Body > 1.5× average
        - Break high/low
        - EMA aligned
        - No big opposite wick
        - Score >= 85
        """
        score = 0
        reasons = []
        direction = "WAIT"
        market_state = features["trend"]
        
        # Base score from trend
        if market_state == "uptrend":
            score += 15
            direction = "CALL"
        elif market_state == "downtrend":
            score += 15
            direction = "PUT"
        else:
            # Range market - lower base score
            score += 5
            market_state = "range"
        
        # ATR spike (strong movement)
        atr_spike = features["atr_spike"]
        if atr_spike >= 1.5:
            score += 20
            reasons.append(f"زخم قوي: ATR spike {atr_spike:.2f}×")
        elif atr_spike >= 1.2:
            score += 10
            reasons.append(f"زخم متوسط: ATR spike {atr_spike:.2f}×")
        else:
            reasons.append(f"⚠️ زخم ضعيف: ATR spike {atr_spike:.2f}×")
        
        # Body strength
        body_strength = features["body_strength"]
        if body_strength >= 1.5:
            score += 20
            reasons.append(f"شمعة قوية: Body {body_strength:.2f}× المتوسط")
        elif body_strength >= 1.2:
            score += 10
            reasons.append(f"شمعة متوسطة: Body {body_strength:.2f}× المتوسط")
        else:
            reasons.append(f"⚠️ شمعة ضعيفة: Body {body_strength:.2f}× المتوسط")
        
        # EMA alignment
        if direction == "CALL" and features["ema_aligned_up"]:
            score += 15
            reasons.append("EMA متصاعدة: EMA9 > EMA21 > EMA50")
        elif direction == "PUT" and features["ema_aligned_down"]:
            score += 15
            reasons.append("EMA متنازلة: EMA9 < EMA21 < EMA50")
        elif direction == "CALL" and features["ema9"] > features["ema21"]:
            score += 8
            reasons.append("EMA9 > EMA21 (اتجاه قصير صاعد)")
        elif direction == "PUT" and features["ema9"] < features["ema21"]:
            score += 8
            reasons.append("EMA9 < EMA21 (اتجاه قصير هابط)")
        
        # Wick check (no big opposite wick)
        upper_wick_ratio = features["upper_wick_ratio"]
        lower_wick_ratio = features["lower_wick_ratio"]
        
        if direction == "CALL" and upper_wick_ratio < 0.3:
            score += 10
            reasons.append("لا يوجد wick علوي كبير")
        elif direction == "PUT" and lower_wick_ratio < 0.3:
            score += 10
            reasons.append("لا يوجد wick سفلي كبير")
        elif direction == "CALL" and upper_wick_ratio >= 0.4:
            score -= 10
            reasons.append("⚠️ wick علوي كبير - مقاومة")
        elif direction == "PUT" and lower_wick_ratio >= 0.4:
            score -= 10
            reasons.append("⚠️ wick سفلي كبير - دعم")
        
        # RSI check
        rsi = features["rsi"]
        if direction == "CALL" and 50 < rsi < 70:
            score += 10
            reasons.append(f"RSI مناسب للشراء: {rsi:.1f}")
        elif direction == "PUT" and 30 < rsi < 50:
            score += 10
            reasons.append(f"RSI مناسب للبيع: {rsi:.1f}")
        elif rsi > 80:
            score -= 10
            reasons.append(f"⚠️ RSI تشبع شرائي: {rsi:.1f}")
        elif rsi < 20:
            score -= 10
            reasons.append(f"⚠️ RSI تشبع بيعي: {rsi:.1f}")
        
        # MACD confirmation
        macd_hist = features["macd_hist"]
        if direction == "CALL" and macd_hist > 0:
            score += 10
            reasons.append("MACD إيجابي - يؤكد الصعود")
        elif direction == "PUT" and macd_hist < 0:
            score += 10
            reasons.append("MACD سلبي - يؤكد الهبوط")
        
        # Final score cap
        score = max(0, min(100, score))
        
        # Create signal
        if score >= TIER_STRONG:
            signal = Signal(
                pair=pair,
                tf=timeframe,
                direction=direction,
                score=score,
                market_state=market_state,
                reasons=reasons,
                features=features
            )
            return signal
        else:
            return None
    
    def _analyze_momentum(
        self,
        pair: str,
        df: pd.DataFrame,
        features: Dict[str, Any],
        timeframe: str
    ) -> Optional[Signal]:
        """
        Analyze for Momentum mode (2-3M)
        
        Requirements:
        - EMA aligned
        - RSI 45-65
        - Clear trend
        - ATR medium-high
        - Score >= 75
        """
        score = 0
        reasons = []
        direction = "WAIT"
        market_state = features["trend"]
        
        # Base score from trend
        if market_state == "uptrend":
            score += 20
            direction = "CALL"
            reasons.append("اتجاه صاعد واضح")
        elif market_state == "downtrend":
            score += 20
            direction = "PUT"
            reasons.append("اتجاه هابط واضح")
        else:
            # Range market - lower score
            score += 8
            market_state = "range"
            reasons.append("⚠️ سوق عرضي (Range)")
        
        # EMA alignment (very important for momentum)
        if direction == "CALL" and features["ema_aligned_up"]:
            score += 25
            reasons.append("EMA متصاعدة بالكامل: EMA9 > EMA21 > EMA50")
        elif direction == "PUT" and features["ema_aligned_down"]:
            score += 25
            reasons.append("EMA متنازلة بالكامل: EMA9 < EMA21 < EMA50")
        elif direction == "CALL" and features["ema9"] > features["ema21"]:
            score += 12
            reasons.append("EMA9 > EMA21 (اتجاه قصير صاعد)")
        elif direction == "PUT" and features["ema9"] < features["ema21"]:
            score += 12
            reasons.append("EMA9 < EMA21 (اتجاه قصير هابط)")
        
        # RSI (not extreme)
        rsi = features["rsi"]
        if 45 <= rsi <= 65:
            score += 15
            reasons.append(f"RSI متوازن: {rsi:.1f} (لا تشبع)")
        elif 40 <= rsi <= 70:
            score += 8
            reasons.append(f"RSI مقبول: {rsi:.1f}")
        elif rsi > 75:
            score -= 10
            reasons.append(f"⚠️ RSI تشبع شرائي: {rsi:.1f}")
        elif rsi < 25:
            score -= 10
            reasons.append(f"⚠️ RSI تشبع بيعي: {rsi:.1f}")
        
        # ATR (medium to high)
        atr_spike = features["atr_spike"]
        if atr_spike >= 1.2:
            score += 15
            reasons.append(f"تقلب جيد: ATR {atr_spike:.2f}×")
        elif atr_spike >= 0.8:
            score += 8
            reasons.append(f"تقلب متوسط: ATR {atr_spike:.2f}×")
        else:
            score -= 5
            reasons.append(f"⚠️ تقلب منخفض: ATR {atr_spike:.2f}×")
        
        # Momentum
        momentum = features["momentum_3"]
        if direction == "CALL" and momentum > 0:
            score += 10
            reasons.append("زخم إيجابي (آخر 3 شموع)")
        elif direction == "PUT" and momentum < 0:
            score += 10
            reasons.append("زخم سلبي (آخر 3 شموع)")
        
        # MACD
        macd_hist = features["macd_hist"]
        if direction == "CALL" and macd_hist > 0:
            score += 10
            reasons.append("MACD إيجابي")
        elif direction == "PUT" and macd_hist < 0:
            score += 10
            reasons.append("MACD سلبي")
        
        # Body strength (not too weak)
        body_strength = features["body_strength"]
        if body_strength >= 1.0:
            score += 5
            reasons.append(f"شمعة قوية: {body_strength:.2f}×")
        elif body_strength < 0.5:
            score -= 5
            reasons.append(f"⚠️ شمعة ضعيفة: {body_strength:.2f}×")
        
        # Final score cap
        score = max(0, min(100, score))
        
        # Create signal
        if score >= TIER_VALID:
            signal = Signal(
                pair=pair,
                tf=timeframe,
                direction=direction,
                score=score,
                market_state=market_state,
                reasons=reasons,
                features=features
            )
            return signal
        else:
            return None
    
    async def scan_all_pairs(
        self,
        pairs_data: Dict[str, pd.DataFrame],
        mode: str,
        timeframe: str
    ) -> List[Signal]:
        """
        Scan all pairs and generate signals
        
        Args:
            pairs_data: Dict mapping pair to DataFrame
            mode: "sniper" or "momentum"
            timeframe: Timeframe
        
        Returns:
            List of Signal objects
        """
        signals = []
        
        for pair, df in pairs_data.items():
            try:
                signal = self.analyze_pair(pair, df, mode, timeframe)
                if signal:
                    signals.append(signal)
                    logger.debug(f"✅ Signal generated for {pair}: {signal.direction} ({signal.score:.0f})")
            except Exception as e:
                logger.error(f"❌ Error analyzing {pair}: {e}")
        
        logger.info(f"✅ Generated {len(signals)} signals from {len(pairs_data)} pairs")
        return signals
