import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Google official SDK ko configure kar rahe hain
genai.configure(api_key=GEMINI_API_KEY)

ADMIN_ID = 5572297184
REQUIRED_CHANNEL = "@A_TOOLSx2"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def is_user_subscribed(user_id: int) -> bool:
    if str(user_id) == str(ADMIN_ID):
        return True
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
    except Exception as e:
        print(f"Error checking channel status: {e}")
        return False
    return False

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        await message.answer("नमस्ते मालिक! JARVIS सक्रिय है।")
        return

    subscribed = await is_user_subscribed(message.from_user.id)
    if not subscribed:
        await message.answer(f"🚀 To use this bot, you must join our channel: https://t.me/A_TOOLSx2")
        return
        
    await message.answer("नमस्ते! मैं JARVIS Bot हूँ। मुझसे कोई भी सवाल पूछिए।")

async def get_gemini_response(prompt: str) -> str:
    try:
        # Ab URL ki koi jhanjhat nahi, official SDK seedha model handle karega
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        return f"त्रुटि: {e}"

@dp.message()
async def handle_message(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        subscribed = await is_user_subscribed(message.from_user.id)
        if not subscribed:
            await message.answer(f"🚀 To use this bot, you must join our channel: https://t.me/A_TOOLSx2")
            return

    response_text = await get_gemini_response(message.text)
    await message.answer(response_text)

async def handle_health_check(request):
    return web.Response(text="JARVIS Bot is running!")

async def main():
    print("JARVIS Bot सक्रिय हो गया है...")
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
