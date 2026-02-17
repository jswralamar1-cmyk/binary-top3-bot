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
        
        # Build message
        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━
🏆 **#{rank} - {signal.pair}**
━━━━━━━━━━━━━━━━━━━━━━━━

{direction_emoji} **الاتجاه:** {direction_text}
⭐ **النقاط:** {signal.score:.0f}/100 {emoji} {tier}
{market_emoji} **حالة السوق:** {market_text}

━━━━━━━━━━━━━━━━━━━━━━━━
📍 **خطة الدخول:**

🎯 **نقطة الدخول:** {signal.trigger_price:.5f} (كسر)
💵 **السعر الحالي:** {signal.current_price:.5f}
📏 **المسافة:** {signal.distance_pips:.1f} نقطة

⏱️ **مدة الصفقة:** {signal.expiry_minutes} دقيقة
🕒 **صالح لمدة:** {signal.validity_seconds} ثانية

━━━━━━━━━━━━━━━━━━━━━━━━
💡 **الأسباب:**

"""
        
        # Add reasons
        for i, reason in enumerate(signal.reasons[:5], 1):  # Max 5 reasons
            message += f"{i}️⃣ {reason}\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Add warnings if any
        if signal.warnings:
            message += "⚠️ **تحذيرات المخاطر:**\n\n"
            for warning in signal.warnings:
                message += f"{warning}\n"
            message += f"\n🛡️ **مستوى المخاطرة:** {signal.risk_level}\n"
            message += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Add instructions
        message += """⚠️ **تعليمات مهمة:**

✅ ادخل فقط إذا تحقق الكسر (Price Trigger)
❌ لا تدخل إذا لم يصل السعر خلال Validity Window
❌ لا تدخل إذا ظهر wick معاكس كبير
"""
        
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
