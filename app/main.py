"""
Binary Top3 Bot - Main Entry Point
MJ Trading - Professional Binary Options Scanner
"""

import os
import sys
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
    
    # Get webhook URL from environment (Render provides this)
    webhook_url = os.getenv("RENDER_EXTERNAL_URL")
    if not webhook_url:
        logger.error("❌ RENDER_EXTERNAL_URL not found! Cannot set webhook.")
        sys.exit(1)
    
    # Build full webhook path
    webhook_path = f"{webhook_url}/webhook"
    
    logger.info("=" * 60)
    logger.info("🚀 Binary Top3 Bot Starting...")
    logger.info("📊 MJ Trading - Professional Binary Options Scanner")
    logger.info("=" * 60)
    logger.info(f"🌐 Webhook URL: {webhook_path}")
    logger.info("=" * 60)
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Setup handlers
    setup_handlers(app)
    
    # Start bot with webhook
    logger.info("✅ Bot is ready!")
    logger.info("🔗 Running in webhook mode")
    logger.info("=" * 60)
    
    # Run webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path="webhook",
        webhook_url=webhook_path,
        drop_pending_updates=True  # Drop old updates
    )


if __name__ == "__main__":
    main()
