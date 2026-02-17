"""
Telegram UI for Binary Top3 Bot
Complete button flow: Mode → Expiry → Timeframe → Start Scan
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from app.config import MODE_SNIPER, MODE_MOMENTUM, EXPIRIES, TIMEFRAMES
from app.models import UserSelection
from app.scanner import Scanner
from app.formatter import Formatter

logger = logging.getLogger(__name__)


# ============================================================================
# Keyboard Builders
# ============================================================================

def build_mode_keyboard() -> InlineKeyboardMarkup:
    """Build mode selection keyboard"""
    buttons = [
        [InlineKeyboardButton("⚡ قناص لحظي (1M Sniper)", callback_data=f"MODE:{MODE_SNIPER}")],
        [InlineKeyboardButton("🔥 زخم قصير (2-3M Momentum)", callback_data=f"MODE:{MODE_MOMENTUM}")]
    ]
    return InlineKeyboardMarkup(buttons)


def build_expiry_keyboard() -> InlineKeyboardMarkup:
    """Build expiry selection keyboard"""
    buttons = []
    for exp in EXPIRIES:
        buttons.append([InlineKeyboardButton(f"⏱️ {exp} دقيقة", callback_data=f"EXPIRY:{exp}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="BACK:mode")])
    return InlineKeyboardMarkup(buttons)


def build_timeframe_keyboard() -> InlineKeyboardMarkup:
    """Build timeframe selection keyboard"""
    tf_labels = {
        "1min": "⏱️ 1 دقيقة",
        "5min": "⏱️ 5 دقائق",
        "15min": "⏱️ 15 دقيقة",
        "1h": "🕐 1 ساعة",
        "4h": "🕓 4 ساعات"
    }
    
    buttons = []
    for tf in TIMEFRAMES:
        label = tf_labels.get(tf, tf)
        buttons.append([InlineKeyboardButton(label, callback_data=f"TF:{tf}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="BACK:expiry")])
    return InlineKeyboardMarkup(buttons)


def build_start_keyboard() -> InlineKeyboardMarkup:
    """Build start scan keyboard"""
    buttons = [
        [InlineKeyboardButton("🚀 بدء الفحص", callback_data="START_SCAN")],
        [InlineKeyboardButton("🔄 إعادة تعيين", callback_data="RESET")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="BACK:timeframe")]
    ]
    return InlineKeyboardMarkup(buttons)


# ============================================================================
# Helper Functions
# ============================================================================

def get_user_selection(context: ContextTypes.DEFAULT_TYPE) -> UserSelection:
    """Get or create user selection from context"""
    if "selection" not in context.user_data:
        context.user_data["selection"] = UserSelection()
    return context.user_data["selection"]


def format_selection_summary(selection: UserSelection) -> str:
    """Format selection summary in Arabic"""
    mode_text = "⚡ قناص لحظي (1M Sniper)" if selection.mode == MODE_SNIPER else "🔥 زخم قصير (2-3M Momentum)"
    expiry_text = f"⏱️ {selection.expiry} دقيقة" if selection.expiry else "❌ لم يتم الاختيار"
    
    tf_labels = {
        "1min": "⏱️ 1 دقيقة",
        "5min": "⏱️ 5 دقائق",
        "15min": "⏱️ 15 دقيقة",
        "1h": "🕐 1 ساعة",
        "4h": "🕓 4 ساعات"
    }
    tf_text = tf_labels.get(selection.timeframe, "❌ لم يتم الاختيار") if selection.timeframe else "❌ لم يتم الاختيار"
    
    return f"""📊 **إعداداتك الحالية:**

🎯 **النمط:** {mode_text}
⏱️ **مدة الصفقة:** {expiry_text}
📈 **الفريم الزمني:** {tf_text}
"""


# ============================================================================
# Command Handlers
# ============================================================================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """👋 **مرحباً بك في MJ Trading Bot!**

🎯 **بوت احترافي للفحص العميق وتوليد إشارات Binary Options**

━━━━━━━━━━━━━━━━━━━━━━━━

🔍 **كيف يعمل البوت:**

1️⃣ اختر النمط (قناص أو زخم)
2️⃣ اختر مدة الصفقة (1 أو 3 دقائق)
3️⃣ اختر الفريم الزمني
4️⃣ ابدأ الفحص

━━━━━━━━━━━━━━━━━━━━━━━━

📊 **المميزات:**

✅ فحص 25 زوج في ثوانٍ
✅ تحليل فني دقيق (RSI, EMA, ATR)
✅ خطة دخول محددة (Price Trigger)
✅ شارت احترافي لكل إشارة
✅ تحذيرات المخاطر والأخبار
✅ Top 3 فرص فقط (قوية)

━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **ابدأ الآن باختيار النمط:**
"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=build_mode_keyboard(),
        parse_mode='Markdown'
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """📖 **دليل الاستخدام:**

━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **الأنماط:**

⚡ **قناص لحظي (1M Sniper):**
- للدخول السريع جداً
- يحتاج كسر قوي + زخم عالي
- Score >= 85
- Validity: 45 ثانية

🔥 **زخم قصير (2-3M Momentum):**
- للصفقات القصيرة
- يحتاج اتجاه واضح + استمرارية
- Score >= 75
- Validity: 90 ثانية

━━━━━━━━━━━━━━━━━━━━━━━━

⭐ **معايير النقاط:**

🔥🔥🔥 85+ = إعداد قوي جداً
🔥🔥   75-84 = إعداد صالح
🔥     70-74 = إعداد جريء
⚠️     < 70 = يتم تجاهله

━━━━━━━━━━━━━━━━━━━━━━━━

💡 **نصائح:**

✅ استخدم فريمات مختلفة للتأكيد
✅ انتبه للتحذيرات (أخبار، سبريد)
✅ ادخل فقط عند تحقق Price Trigger
✅ لا تدخل بعد انتهاء Validity Window

━━━━━━━━━━━━━━━━━━━━━━━━

🔧 **الأوامر:**

/start - بدء البوت
/help - هذا الدليل
/scan - بدء فحص جديد
/reset - إعادة تعيين الإعدادات
"""
    
    await update.message.reply_text(
        help_message,
        reply_markup=build_mode_keyboard(),
        parse_mode='Markdown'
    )


async def scan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /scan command"""
    selection = get_user_selection(context)
    
    if selection.is_complete():
        summary = format_selection_summary(selection)
        await update.message.reply_text(
            f"{summary}\n✅ **جاهز للفحص!**",
            reply_markup=build_start_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🔍 **اختر النمط للبدء:**",
            reply_markup=build_mode_keyboard(),
            parse_mode='Markdown'
        )


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command"""
    context.user_data.clear()
    
    await update.message.reply_text(
        "🔄 **تم إعادة تعيين الإعدادات!**\n\n🚀 **ابدأ من جديد:**",
        reply_markup=build_mode_keyboard(),
        parse_mode='Markdown'
    )


# ============================================================================
# Callback Handlers
# ============================================================================

async def mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mode selection"""
    query = update.callback_query
    await query.answer()
    
    mode = query.data.split(":")[1]
    selection = get_user_selection(context)
    selection.mode = mode
    
    mode_text = "⚡ قناص لحظي (1M Sniper)" if mode == MODE_SNIPER else "🔥 زخم قصير (2-3M Momentum)"
    
    message = f"""✅ **تم اختيار النمط:** {mode_text}

⏱️ **الآن اختر مدة الصفقة:**
"""
    
    await query.edit_message_text(
        message,
        reply_markup=build_expiry_keyboard(),
        parse_mode='Markdown'
    )


async def expiry_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle expiry selection"""
    query = update.callback_query
    await query.answer()
    
    expiry = int(query.data.split(":")[1])
    selection = get_user_selection(context)
    selection.expiry = expiry
    
    summary = format_selection_summary(selection)
    message = f"""{summary}

📈 **الآن اختر الفريم الزمني:**
"""
    
    await query.edit_message_text(
        message,
        reply_markup=build_timeframe_keyboard(),
        parse_mode='Markdown'
    )


async def timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle timeframe selection"""
    query = update.callback_query
    await query.answer()
    
    tf = query.data.split(":")[1]
    selection = get_user_selection(context)
    selection.timeframe = tf
    
    summary = format_selection_summary(selection)
    message = f"""{summary}

✅ **الإعدادات كاملة!**

🚀 **اضغط "بدء الفحص" للبدء:**
"""
    
    await query.edit_message_text(
        message,
        reply_markup=build_start_keyboard(),
        parse_mode='Markdown'
    )


async def start_scan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start scan button"""
    query = update.callback_query
    await query.answer()
    
    selection = get_user_selection(context)
    
    if not selection.is_complete():
        await query.edit_message_text(
            "❌ **الرجاء إكمال جميع الإعدادات أولاً!**",
            reply_markup=build_mode_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Show "scanning" message
    summary = format_selection_summary(selection)
    scanning_message = f"""{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

🔍 **جاري فحص 25 زوج...**

⏳ يرجى الانتظار (30-60 ثانية)...

━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await query.edit_message_text(
        scanning_message,
        parse_mode='Markdown'
    )
    
    try:
        # Initialize scanner and formatter
        scanner = Scanner()
        formatter = Formatter()
        
        # Perform scan
        result = await scanner.scan(selection)
        
        # Format messages
        messages = formatter.format_scan_result(result)
        
        # Send summary
        await query.edit_message_text(
            messages[0],
            parse_mode="Markdown"
        )
        
        # Send signals with charts
        for i, signal in enumerate(result.signals, 1):
            # Send chart if available
            if signal.chart_path:
                try:
                    with open(signal.chart_path, 'rb') as chart_file:
                        await context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=chart_file,
                            caption=messages[i],
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logger.error(f"❌ Error sending chart: {e}")
                    # Send text only if chart failed
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=messages[i],
                        parse_mode="Markdown"
                    )
            else:
                # Send text only if chart not generated
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=messages[i],
                    parse_mode="Markdown"
                )
        
        # Show menu again
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🔄 **فحص جديد؟**",
            reply_markup=build_mode_keyboard(),
            parse_mode="Markdown"
        )
    
    except Exception as e:
        logger.error(f"❌ Error during scan: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ **حدث خطأ أثناء الفحص:**\n\n`{str(e)}`\n\n"
            f"الرجاء المحاولة مرة أخرى.",
            reply_markup=build_mode_keyboard(),
            parse_mode="Markdown"
        )


async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reset button"""
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    
    await query.edit_message_text(
        "🔄 **تم إعادة تعيين الإعدادات!**\n\n🚀 **ابدأ من جديد:**",
        reply_markup=build_mode_keyboard(),
        parse_mode='Markdown'
    )


async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button"""
    query = update.callback_query
    await query.answer()
    
    target = query.data.split(":")[1]
    selection = get_user_selection(context)
    
    if target == "mode":
        # Go back to mode selection
        await query.edit_message_text(
            "🔍 **اختر النمط:**",
            reply_markup=build_mode_keyboard(),
            parse_mode='Markdown'
        )
    
    elif target == "expiry":
        # Go back to expiry selection
        mode_text = "⚡ قناص لحظي (1M Sniper)" if selection.mode == MODE_SNIPER else "🔥 زخم قصير (2-3M Momentum)"
        message = f"""✅ **النمط المختار:** {mode_text}

⏱️ **اختر مدة الصفقة:**
"""
        await query.edit_message_text(
            message,
            reply_markup=build_expiry_keyboard(),
            parse_mode='Markdown'
        )
    
    elif target == "timeframe":
        # Go back to timeframe selection
        summary = format_selection_summary(selection)
        message = f"""{summary}

📈 **اختر الفريم الزمني:**
"""
        await query.edit_message_text(
            message,
            reply_markup=build_timeframe_keyboard(),
            parse_mode='Markdown'
        )


# ============================================================================
# Application Setup
# ============================================================================

def setup_handlers(app: Application):
    """Setup all handlers"""
    # Commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("scan", scan_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(mode_callback, pattern=r"^MODE:"))
    app.add_handler(CallbackQueryHandler(expiry_callback, pattern=r"^EXPIRY:"))
    app.add_handler(CallbackQueryHandler(timeframe_callback, pattern=r"^TF:"))
    app.add_handler(CallbackQueryHandler(start_scan_callback, pattern=r"^START_SCAN$"))
    app.add_handler(CallbackQueryHandler(reset_callback, pattern=r"^RESET$"))
    app.add_handler(CallbackQueryHandler(back_callback, pattern=r"^BACK:"))
    
    logger.info("✅ Telegram UI handlers registered")
