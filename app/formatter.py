"""
Formatter - Formats signals for Telegram messages
"""

import logging
from typing import List

from app.models import Signal, ScanResult
from app.ranking_engine import RankingEngine

logger = logging.getLogger(__name__)


class Formatter:
    """Message formatter"""
    
    def __init__(self):
        self.ranking_engine = RankingEngine()
        logger.info("✅ Formatter initialized")
    
    def format_signal(self, signal: Signal, rank: int) -> str:
        """
        Format a single signal for Telegram
        
        Args:
            signal: Signal object
            rank: Rank (1, 2, 3)
        
        Returns:
            Formatted message
        """
        # Get tier
        emoji, tier = self.ranking_engine.get_tier(signal.score)
        
        # Direction emoji
        if signal.direction == "CALL":
            direction_emoji = "📈"
            direction_text = "شراء (CALL)"
        else:
            direction_emoji = "📉"
            direction_text = "بيع (PUT)"
        
        # Market state
        if signal.market_state == "uptrend":
            market_emoji = "📈"
            market_text = "اتجاه صاعد"
        elif signal.market_state == "downtrend":
            market_emoji = "📉"
            market_text = "اتجاه هابط"
        else:
            market_emoji = "↔️"
            market_text = "سوق عرضي (Range)"
        
        # Build message (shortened)
        message = f"""🏆 **#{rank} - {signal.pair}** {emoji}

{direction_emoji} **{direction_text}** | ⭐ {signal.score:.0f}/100

📍 **الدخول:** {signal.trigger_price:.5f} (الحالي: {signal.current_price:.5f})
⏱️ **المدة:** {signal.expiry_minutes}د | 🕒 **صالح:** {signal.validity_seconds}ث

💡 **السبب:**
"""
        
        # Add top 2 reasons only
        for i, reason in enumerate(signal.reasons[:2], 1):
            message += f"{i}️⃣ {reason}\n"
        
        # Add warnings if critical
        if signal.warnings:
            message += f"\n⚠️ {signal.warnings[0]}"  # Only first warning
        
        message += "\n\n✅ **ادخل عند الكسر فقط**"
        
        return message
    
    def format_scan_result(self, result: ScanResult) -> List[str]:
        """
        Format scan result for Telegram
        
        Args:
            result: ScanResult object
        
        Returns:
            List of messages (one per signal + summary)
        """
        messages = []
        
        # Summary message
        mode_text = "⚡ قناص لحظي (1M Sniper)" if result.mode == "sniper" else "🔥 زخم قصير (2-3M Momentum)"
        
        summary = f"""✅ **اكتمل الفحص!**

━━━━━━━━━━━━━━━━━━━━━━━━
📊 **ملخص الفحص:**

🎯 **النمط:** {mode_text}
⏱️ **مدة الصفقة:** {result.expiry} دقيقة
📈 **الفريم الزمني:** {result.timeframe}
🕒 **وقت الفحص:** {result.scan_time}

━━━━━━━━━━━━━━━━━━━━━━━━
📊 **النتائج:**

🔍 **تم فحص:** {result.total_pairs} زوج
✅ **مرشحات:** {result.filtered_count} إشارة
🏆 **Top 3:** {len(result.signals)} إشارة

━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if not result.signals:
            summary += "\n⚠️ **لا توجد إشارات قوية في الوقت الحالي.**\n\n💡 **جرب:**\n- فريم زمني مختلف\n- نمط مختلف\n- انتظر حركة أقوى في السوق"
            messages.append(summary)
        else:
            summary += f"\n🎉 **وجدنا {len(result.signals)} فرص قوية!**\n\n⬇️ **تفاصيل الإشارات:**"
            messages.append(summary)
            
            # Add signal messages
            for i, signal in enumerate(result.signals, 1):
                signal_msg = self.format_signal(signal, i)
                messages.append(signal_msg)
        
        return messages
