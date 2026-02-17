"""
Binary Top3 Bot - Main Entry Point
MJ Trading - Professional Binary Options Scanner
"""

import os
import sys
import fcntl
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
    # Instance lock (prevent multiple instances)
    lock_file = "/tmp/binary_top3_bot.lock"
    try:
        lock_fd = open(lock_file, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        logger.info("✅ Instance lock acquired (PID: {})".format(os.getpid()))
    except IOError:
        logger.error("❌ Another instance is already running!")
        sys.exit(1)
    
    # Check token
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("❌ Missing TELEGRAM_BOT_TOKEN environment variable")
    
    logger.info("=" * 60)
    logger.info("🚀 Binary Top3 Bot Starting...")
    logger.info("📊 MJ Trading - Professional Binary Options Scanner")
    logger.info("=" * 60)
    
    # Create application with post_init to clear webhook
    async def post_init(application):
        """Clear webhook before starting polling"""
        try:
            logger.info("🧹 Clearing webhook and pending updates...")
            await application.bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ Webhook cleared successfully")
        except Exception as e:
            logger.warning(f"⚠️ Webhook clear warning: {e}")
    
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Setup handlers
    setup_handlers(app)
    
    # Start bot
    logger.info("✅ Bot is ready!")
    logger.info("🔍 Running in polling mode")
    logger.info("=" * 60)
    
    # Run polling with drop_pending_updates to prevent conflicts
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # Drop old updates to prevent conflicts
    )


if __name__ == "__main__":
    main()
