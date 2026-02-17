# Binary Top3 Bot - MJ Trading

**Professional Binary Options Scanner with Smart Charts & Risk Management**

## 🎯 Features

- ⚡ **Sniper Mode** (1M) - للدخول اللحظي السريع
- 🔥 **Momentum Mode** (2-3M) - للصفقات القصيرة
- 📊 **Smart Charts** - شارت احترافي لكل إشارة
- 🎯 **Price Trigger** - خطة دخول محددة
- ⚠️ **Risk Warnings** - تحذيرات الأخبار والسبريد
- 🔍 **Deep Scan** - فحص 25 زوج في ثوانٍ
- 🏆 **Top 3 Only** - أفضل 3 فرص فقط

## 📊 Strategy Tiers

- 🔥🔥🔥 **85+** = Strong Setup
- 🔥🔥 **75-84** = Valid Setup
- 🔥 **70-74** = Aggressive Setup
- ⚠️ **< 70** = Ignored

## 🏗️ Architecture

```
binary_top3_bot/
├── app/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration
│   ├── models.py            # Data models
│   ├── telegram_ui.py       # Telegram UI (Phase B ✅)
│   ├── data_provider.py     # TwelveData API (Phase C)
│   ├── indicators.py        # Technical indicators (Phase D)
│   ├── signal_engine.py     # Signal generation (Phase E)
│   ├── confirm_engine.py    # 5m confirmation (Phase F)
│   ├── entry_engine.py      # Price trigger logic (Phase G)
│   ├── ranking_engine.py    # Top3 ranking (Phase H)
│   ├── risk_engine.py       # News & spread warnings (Phase I)
│   └── chart_generator.py   # Smart charts (Phase J)
├── requirements.txt
├── Dockerfile
└── render.yaml
```

## 🚀 Current Status

### ✅ Phase A: Structure + Docker + Render (DONE)
- Project structure created
- Docker configuration
- Render deployment config

### ✅ Phase B: Telegram UI (DONE)
- Complete button flow: Mode → Expiry → Timeframe → Start
- Arabic messages
- User selection storage

### ⏳ Phase C-J: Coming Soon
- Data Provider (TwelveData API)
- Indicators (RSI, EMA, ATR)
- Signal Engine
- Confirm Engine (5m optional)
- Entry Engine (Price Trigger)
- Ranking Engine (Top3)
- Risk Engine (News + Spread)
- Chart Generator (Smart Charts)

## 📦 Installation

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd binary_top3_bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export TWELVEDATA_API_KEY="your_key"
export AI_API_KEY="your_groq_key"

# Run bot
python -m app.main
```

### Docker

```bash
# Build image
docker build -t binary-top3-bot .

# Run container
docker run -e TELEGRAM_BOT_TOKEN="..." \
           -e TWELVEDATA_API_KEY="..." \
           -e AI_API_KEY="..." \
           binary-top3-bot
```

### Deploy on Render

1. Push code to GitHub
2. Create Web Service on Render
3. Connect GitHub repository
4. Add Environment Variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TWELVEDATA_API_KEY`
   - `AI_API_KEY`
5. Deploy!

## 🎮 Usage

1. Start bot: `/start`
2. Choose mode: ⚡ Sniper or 🔥 Momentum
3. Choose expiry: 1 or 3 minutes
4. Choose timeframe: 1m, 5m, 15m, 1h, 4h
5. Start scan: 🚀 بدء الفحص
6. Wait for results (10-30 seconds)
7. Review Top 3 signals with charts

## 📋 Commands

- `/start` - بدء البوت
- `/help` - دليل الاستخدام
- `/scan` - بدء فحص جديد
- `/reset` - إعادة تعيين الإعدادات

## 🔧 Configuration

Edit `app/config.py` to customize:
- Trading pairs (25 pairs)
- Timeframes
- Expiry options
- Scoring thresholds
- Chart settings
- Risk settings

## 📊 Modes

### ⚡ Sniper Mode (1M)
- For ultra-fast entries
- Requires strong breakout + high momentum
- Score >= 85
- Validity: 45 seconds
- Chart: 50 candles + EMA9/21 + RSI

### 🔥 Momentum Mode (2-3M)
- For short-term trades
- Requires clear trend + continuation
- Score >= 75
- Validity: 90 seconds
- Chart: 100 candles + EMA9/21/50 + RSI/MACD

## 🛡️ Risk Management

- ⚠️ News warnings (±30 min window)
- ⚠️ Spread warnings (high spread detection)
- ⚠️ Range market detection
- ⚠️ Validity window enforcement

## 📈 Technical Indicators

- RSI (14)
- EMA (9, 21, 50)
- ATR (14)
- MACD
- Body/Wick ratio
- Momentum (3 candles)

## 🎨 Chart Features

- Dark theme
- Candlestick chart
- EMA lines (colored)
- Entry trigger line
- Support/Resistance zones
- Annotations (score, expiry, validity)
- MJ Trading watermark

## 📄 License

MIT

## 👨‍💻 Author

**MJ Trading**
Professional Binary Options Scanner
