"""
Configuration for Binary Top3 Bot
"""

import os

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# TwelveData API
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
TWELVEDATA_API_URL = "https://api.twelvedata.com/time_series"

# Groq AI
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Trading Pairs (25 pairs)
TRADING_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
    "USD/CAD", "NZD/USD", "EUR/GBP", "EUR/JPY", "EUR/CHF",
    "EUR/AUD", "EUR/CAD", "EUR/NZD", "GBP/JPY", "GBP/CHF",
    "GBP/AUD", "GBP/CAD", "GBP/NZD", "AUD/JPY", "AUD/CHF",
    "AUD/CAD", "AUD/NZD", "CAD/JPY", "CHF/JPY", "NZD/JPY"
]

# Timeframes
TIMEFRAMES = ["1min", "5min", "15min", "1h", "4h"]

# Expiry options (minutes)
EXPIRIES = [1, 3]

# Scoring
MIN_SCORE = 65
MAX_RESULTS = 3

# Strategy Tiers
TIER_STRONG = 85  # 🔥🔥🔥
TIER_VALID = 75   # 🔥🔥
TIER_AGGRESSIVE = 70  # 🔥

# Modes
MODE_SNIPER = "sniper"
MODE_MOMENTUM = "momentum"

# Brand
BRAND_NAME = "MJ Trading"
WATERMARK_TEXT = "MJ Trading"

# Chart settings
CHART_CANDLES_SNIPER = 50
CHART_CANDLES_MOMENTUM = 100

# Entry trigger settings
TRIGGER_BUFFER_MULTIPLIER = 0.15  # 15% of ATR
VALIDITY_1M = 45  # seconds
VALIDITY_3M = 90  # seconds

# Risk settings
NEWS_WARNING_WINDOW = 30  # minutes before/after news
MAX_SPREAD_MULTIPLIER = 3.0  # max spread = 3× average spread

# API settings
API_TIMEOUT = 10  # seconds
API_RETRY = 2
API_SEMAPHORE = 6  # concurrent requests
