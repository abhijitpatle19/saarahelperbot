import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test_bot():
    """Test if the bot token is valid"""
    try:
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot is working!")
        print(f"🤖 Bot name: {me.first_name}")
        print(f"📝 Bot username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing bot connection...")
    asyncio.run(test_bot())
