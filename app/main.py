"""
Binary Top3 Bot - Main Entry Point
MJ Trading - Professional Binary Options Scanner
"""

import os
import logging
from telegram import Update
from telegram.ext import Application

from app.config import TELEGRAM_BOT_TOKEN
from app.telegram_ui import setup_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    # Check token
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("❌ Missing TELEGRAM_BOT_TOKEN environment variable")
    
    logger.info("=" * 60)
    logger.info("🚀 Binary Top3 Bot Starting...")
    logger.info("📊 MJ Trading - Professional Binary Options Scanner")
    logger.info("=" * 60)
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Setup handlers
    setup_handlers(app)
    
    # Start bot
    logger.info("✅ Bot is ready!")
    logger.info("🔍 Running in polling mode")
    logger.info("=" * 60)
    
    # Run polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
