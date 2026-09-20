import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Token va Admin ID
API_TOKEN = "8938280108:AAEkHbfii44vTJlvIR9rhfeoEZ9oA-4Hr04"
ADMIN_ID = 8243336938

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher yaratish
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Start komandasi
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Assalomu alaykum, Admin! Xush kelibsiz.")
    else:
        await message.answer("Assalomu alaykum! O'quv materiallari botiga xush kelibsiz.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
