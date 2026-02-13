#!/usr/bin/env python3
"""
Test Telegram Notification
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def test_telegram():
    """Test Telegram bot configuration"""
    print("=" * 60)
    print("Testing Telegram Configuration")
    print("=" * 60)
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        print("\nHow to setup:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot and follow instructions")
        print("3. Copy the token to .env file")
        return False
    
    if not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID not set in .env")
        print("\nHow to get Chat ID:")
        print("1. Send a message to your bot")
        print("2. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
        print("3. Look for 'chat':{'id': YOUR_CHAT_ID}")
        return False
    
    print(f"✅ Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"✅ Chat ID: {TELEGRAM_CHAT_ID}")
    
    # Test sending message
    print("\nSending test message...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🧪 <b>Test Message</b>\n\nTelegram notification is working!",
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Message sent successfully!")
                print("Check your Telegram to see the message")
                return True
            else:
                print(f"❌ Failed to send: {response.status_code}")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_telegram())
    
    if result:
        print("\n🎉 Telegram is configured correctly!")
    else:
        print("\n⚠️ Please configure Telegram in .env file")
        print("Copy .env.example to .env and fill in your credentials")
