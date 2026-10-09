
  import asyncio
import os
from aiohttp import web
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TELEGRAM_BOT_TOKEN = "8769661200:AAH4-qYLserNJIFbxCcY9NfVjlafDxei7xQ"
# यहाँ AI Studio वाली अपनी पूरी AQ.Ab8... वाली Key पेस्ट करें
GEMINI_API_KEY = "AQ.Ab8RN6IsBli1n9xN0wjB86rGcqNGICc..." 

genai.configure(api_key=GEMINI_API_KEY)
# मॉडल का नाम सही कर दिया गया है
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("नमस्ते! मैं JARVIS Bot हूँ। मुझसे कोई भी सवाल पूछिए।")

@dp.message()
async def handle_message(message: types.Message):
    try:
        response = await model.generate_content_async(message.text)
        await message.answer(response.text)
    except Exception as e:
        print(f"Error detail: {e}")
        await message.answer(f"त्रुटि (Error) आई है:\n{e}")

# Render Web Service के लिए हेल्थ चेक
async def handle_health_check(request):
    return web.Response(text="JARVIS Bot is running!")

async def main():
    print("JARVIS Bot सक्रिय (active) हो गया है...")
    
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

