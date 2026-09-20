import asyncio
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8938280108:AAEkHbfii44vTJlvIR9rhfeoEZ9oA-4Hr04"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
keyboard.add(
    KeyboardButton("📚 Grammar"),
    KeyboardButton("🎧 Listening"),
    KeyboardButton("📖 Reading"),
    KeyboardButton("🗣 Speaking"),
    KeyboardButton("✍️ Writing"),
    KeyboardButton("🧠 Vocabulary"),
    KeyboardButton("🎯 CEFR / Multilevel"),
    KeyboardButton("📄 Real exam's materials"),
    KeyboardButton("📁 Useful Materials"),
    KeyboardButton("ℹ️ About Me")
)

@dp.message_handler(Command("start"))
async def start_handler(message: types.Message):
    welcome_text = (
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "🇬🇧 English Materials Botimizga xush kelibsiz! 🚀\n"
        "Bu yerda ingliz tilini o'rganishingiz va imtihonlarga tayyorgarlik ko'rishingiz uchun barcha kerakli materiallar mavjud.\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in [
    "📚 Grammar", "🎧 Listening", "📖 Reading", "🗣 Speaking",
    "✍️ Writing", "🧠 Vocabulary", "🎯 CEFR / Multilevel",
    "📄 Real exam's materials", "📁 Useful Materials", "ℹ️ About Me"
])
async def sections_handler(message: types.Message):
    text = message.text
    if text == "📚 Grammar":
        await message.answer("📚 **Grammar bo'limi**\n\nBu yerda grammatika qoidalari va qo'llanmalar joylanadi.")
    elif text == "🎧 Listening":
        await message.answer("🎧 **Listening bo'limi**\n\nAudio materiallar va testlar.")
    elif text == "📖 Reading":
        await message.answer("📖 **Reading bo'limi**\n\nMatnlar va kitoblar.")
    elif text == "🗣 Speaking":
        await message.answer("🗣 **Speaking bo'limi**\n\nSo'zlashuv materiallari va savollar.")
    elif text == "✍️ Writing":
        await message.answer("✍️ **Writing bo'limi**\n\nTask 1 va Task 2 uchun namunalar.")
    elif text == "🧠 Vocabulary":
        await message.answer("🧠 **Vocabulary bo'limi**\n\nEng kerakli so'zlar ro'yxati.")
    elif text == "🎯 CEFR / Multilevel":
        await message.answer("🎯 **CEFR / Multilevel**\n\nImtihon formatidagi testlar.")
    elif text == "📄 Real exam's materials":
        await message.answer("📄 **Real exam's materials**\n\nBu bo'limda haqiqiy imtihonlarda tushgan real savollar, materiallar va testlar joylashtiriladi.")
    elif text == "📁 Useful Materials":
        await message.answer("📁 **Useful Materials**\n\nQo'shimcha foydali fayllar.")
    elif text == "ℹ️ About Me":
        await message.answer("ℹ️ **About Me**\n\nUshbu bot ingliz tilini o'rganuvchilar uchun yaratilgan.\nAdmin: @admin_username")

if __name__ == "__main__":
    from aiogram import executor
    print("Bot tayyor!")
    executor.start_polling(dp)

~ 
