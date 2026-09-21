import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

API_TOKEN = '8938280108:AAEC4Bnkvf2PW1xdjRyhKa2qkpdY6n-dN-0'
ADMIN_ID = 8243336938
ADMIN_USERNAME = "@narzullayevich_2010"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Ma'lumotlar xotirasi (RAM)
database = {
    'reading': {'files': [], 'videos': []},
    'writing': {'files': [], 'videos': []},
    'listening': {'files': [], 'videos': []},
    'speaking': {'files': [], 'videos': []},
    'vocabulary': {'files': [], 'videos': []},
    'grammar': {'files': [], 'videos': []},
    'cefr': {'files': [], 'videos': []},
    'exam': {'files': [], 'videos': []},
    'useful': {'files': [], 'videos': []}
}

channels = []
user_states = {}

# --- RENDER DUMMY WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot runs 24/7 successfully!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- MENYU BUYRUQLARINI SOZLASH (Menu tugmasi uchun) ---
async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "🤖 Botni qayta ishga tushirish"),
        BotCommand("admin", "⚙️ Admin panel (Faqat admin uchun)"),
        BotCommand("addchan", "➕ Reklama kanalini qo'shish"),
        BotCommand("delchan", "➖ Reklama kanalini olib tashlash")
    ])

# --- MENYULAR ---
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📚 Reading", callback_data="category_reading"),
        InlineKeyboardButton("✍️ Writing", callback_data="category_writing"),
        InlineKeyboardButton("🎧 Listening", callback_data="category_listening"),
        InlineKeyboardButton("🗣 Speaking", callback_data="category_speaking"),
        InlineKeyboardButton("🧠 Vocabulary", callback_data="category_vocabulary"),
        InlineKeyboardButton("📖 Grammar", callback_data="category_grammar"),
        InlineKeyboardButton("🎯 CEFR / Multilevel", callback_data="category_cefr"),
        InlineKeyboardButton("📄 Real exam's materials", callback_data="category_exam"),
        InlineKeyboardButton("📂 Useful Materials", callback_data="category_useful"),
        InlineKeyboardButton("ℹ️ About Me", callback_data="about_me"),
        InlineKeyboardButton("💬 Biz bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
    )
    return keyboard

def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    categories = [
        ("Reading", "reading"), ("Writing", "writing"),
        ("Listening", "listening"), ("Speaking", "speaking"),
        ("Vocabulary", "vocabulary"), ("Grammar", "grammar"),
        ("CEFR", "cefr"), ("Real Exam", "exam"), ("Useful", "useful")
    ]
    for name, cat in categories:
        keyboard.add(InlineKeyboardButton(f"➕ {name}", callback_data=f"add_{cat}"))
    return keyboard

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 **Xush kelibsiz!**\n\nIngliz tilini mukammal o'rganishingiz uchun barcha zaruriy materiallar to'plangan portalga xush kelibsiz. Kerakli bo'limni tanlang:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ **Admin Panel:** Material qo'shmoqchi bo'lgan bo'limni tanlang:", reply_markup=get_admin_keyboard())
    else:
        await message.answer("⛔ Siz admin emassiz!")

# About Me Bo'limi
@dp.callback_query_handler(text="about_me")
async def process_about(callback: types.CallbackQuery):
    about_text = (
        "✨ **English Materials Bot**\n\n"
        "📖 **Bizning maqsadimiz:**\n"
        "Ushbu loyiha yoshlar, talabalar va ingliz tilini o'rganuvchilarga sifatli va foydali o'quv materiallarini bepul va qulay tarzda taqdim etish maqsadida yaratilgan.\n\n"
        "⚖️ **Mualliflik huquqlariga hurmat:**\n"
        "Botdagi barcha manbalar va intellektual mulk egalarining mualliflik huquqlari to'liq hurmat qilinadi. Barcha fayllar faqat ma'rifiy va ta'limiy maqsadlarda foydalaniladi.\n\n"
        "🚀 *Ilm izlashdan hech qachon to'xtamang!*"
    )
    await callback.message.answer(about_text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('category_'))
async def process_category(callback: types.CallbackQuery):
    cat = callback.data.split('_')[1]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📁 Fayllar", callback_data=f"list_files_{cat}"),
        InlineKeyboardButton("🎬 Videolar", callback_data=f"list_videos_{cat}"),
        InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_main")
    )
    await callback.message.edit_text(f"📂 **{cat.capitalize()}** bo'limi. Turini tanlang:", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query_handler(text="back_to_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Kerakli bo'limni tanlang:", reply_markup=get_main_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('list_'))
async def list_items(callback: types.CallbackQuery):
    _, item_type, cat = callback.data.split('_')
    items = database[cat][item_type]
    
    if not items:
        await callback.message.answer("⚠️ Hozircha bu bo'limda materiallar mavjud emas.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for idx, item in enumerate(items):
        keyboard.add(InlineKeyboardButton(f"📄 {item['title']}", callback_data=f"get_{cat}_{item_type}_{idx}"))
    keyboard.add(InlineKeyboardButton("⬅️ Orqaga", callback_data=f"category_{cat}"))
    
    await callback.message.edit_text(f"📋 **{cat.capitalize()} ({item_type})** ro'yxati:", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data.startswith('get_'))
async def get_item(callback: types.CallbackQuery):
    _, cat, item_type, idx = callback.data.split('_')
    item = database[cat][item_type][int(idx)]
    
    if item_type == 'files':
        await callback.message.answer_document(item['file_id'], caption=item['caption'])
    else:
        await callback.message.answer_video(item['file_id'], caption=item['caption'])
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('add_'))
async def add_item_start(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cat = callback.data.split('_')[1]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📁 Fayl qo'shish", callback_data=f"upload_files_{cat}"),
        InlineKeyboardButton("🎬 Video qo'shish", callback_data=f"upload_videos_{cat}")
    )
    await callback.message.answer(f"➕ **{cat.capitalize()}** bo'limiga nima qo'shasiz?", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data.startswith('upload_'))
async def upload_prompt(callback: types.CallbackQuery):
    _, item_type, cat = callback.data.split('_')
    user_states[callback.from_user.id] = {'cat': cat, 'type': item_type}
    await callback.message.answer(f"Iltimos, {cat} uchun **{item_type[:-1]}** faylini izohi (caption) bilan yuboring:")
    await callback.answer()

@dp.message_handler(content_types=[types.ContentType.DOCUMENT, types.ContentType.VIDEO])
async def handle_upload(message: types.Message):
    if message.from_user.id not in user_states:
        return
    
    state = user_states.pop(message.from_user.id)
    cat = state['cat']
    item_type = state['type']
    
    caption = message.caption or "Material"
    title = caption.split('\n')[0][:30]
    
    file_id = message.document.file_id if message.document else message.video.file_id
    
    database[cat][item_type].append({
        'file_id': file_id,
        'title': title,
        'caption': caption
    })
    await message.answer("✅ Material muvaffaqiyatli saqlandi!")

@dp.message_handler(commands=['addchan'])
async def add_channel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        channel = message.get_args()
        if channel:
            channels.append(channel)
            await message.answer(f"✅ Kanal qo'shildi: {channel}")
        else:
            await message.answer("Format: `/addchan @kanalname`", parse_mode="Markdown")

@dp.message_handler(commands=['delchan'])
async def del_channel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        channel = message.get_args()
        if channel in channels:
            channels.remove(channel)
            await message.answer(f"❌ Kanal olib tashlandi: {channel}")
        else:
            await message.answer("Kanal topilmadi. Format: `/delchan @kanalname`", parse_mode="Markdown")

# --- STARTUP LOGIC (Polling + Web Server + Menu) ---
async def on_startup(dp):
    await set_default_commands(dp)
    asyncio.create_task(web_server())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
