import asyncio
import os
from aiohttp import web, ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # Yeh zaroori hai!

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
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    async with ClientSession() as session:
        async with session.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload) as resp:
            data = await resp.json()
            if resp.status == 200:
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    return "क्षमा करें, उत्तर प्राप्त करने में समस्या आई।"
            else:
                error_msg = data.get("error", {}).get("message", "Unknown error")
                return f"त्रुटि (Error {resp.status}):\n{error_msg}"

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
