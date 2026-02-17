"""
Cleanup Webhook Script
Run this before starting the bot to ensure no webhook conflicts
"""

import requests
import sys
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not found!")
    sys.exit(1)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def delete_webhook():
    """Delete webhook and drop pending updates"""
    print("🧹 Deleting webhook...")
    
    url = f"{BASE_URL}/deleteWebhook"
    params = {"drop_pending_updates": True}
    
    try:
        response = requests.post(url, params=params, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook deleted successfully!")
            print(f"   Description: {result.get('description', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_webhook_info():
    """Get current webhook info"""
    print("🔍 Checking webhook info...")
    
    url = f"{BASE_URL}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            info = result.get("result", {})
            print(f"   URL: {info.get('url', 'None')}")
            print(f"   Pending updates: {info.get('pending_update_count', 0)}")
            print(f"   Last error: {info.get('last_error_message', 'None')}")
            return info
        else:
            print(f"❌ Failed to get webhook info: {result}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Telegram Webhook Cleanup")
    print("=" * 60)
    
    # Get current webhook info
    info = get_webhook_info()
    
    # Delete webhook
    success = delete_webhook()
    
    # Verify
    print("\n🔍 Verifying...")
    info = get_webhook_info()
    
    if info and not info.get("url"):
        print("\n✅ Webhook cleanup successful! Bot is ready for polling.")
        sys.exit(0)
    else:
        print("\n⚠️ Webhook may still be active. Check manually.")
        sys.exit(1)
