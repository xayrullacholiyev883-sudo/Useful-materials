import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Siz taqdim etgan ma'lumotlar
API_TOKEN = "8938280108:AAEzPOqkhPfniqjd7ZW1xwzzv44PmPsYjz0"
ADMIN_ID = 8243336938
ADMIN_USERNAME = "narzullayevich_2010"

# Majburiy obuna kanallari (Hozircha bo'sh, reklama uchun /addchan ishlatasiz)
REQUIRED_CHANNELS = []

# Ma'lumotlar bazasi: Har bir element {"file_id": "...", "title": "..."} ko'rinishida saqlanadi
DATABASE = {
    "reading_files": [], "reading_videos": [],
    "writing_files": [], "writing_videos": [],
    "listening_files": [], "listening_videos": [],
    "speaking_files": [], "speaking_videos": []
}

ADMIN_STATE = {}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_subscriptions(user_id: int):
    if not REQUIRED_CHANNELS:
        return True
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True

def get_main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📚 Reading", callback_data="main_reading"),
        InlineKeyboardButton("✍️ Writing", callback_data="main_writing"),
        InlineKeyboardButton("🎧 Listening", callback_data="main_listening"),
        InlineKeyboardButton("🗣 Speaking", callback_data="main_speaking"),
        InlineKeyboardButton("📞 Biz bilan bog'lanish", callback_data="contact_admin"),
        InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscriptions(user_id):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for channel in REQUIRED_CHANNELS:
            keyboard.add(InlineKeyboardButton(f"📢 {channel} kanaliga qo'shilish", url=f"https://t.me/{channel.replace('@', '')}"))
        keyboard.add(InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub"))
        await message.answer("🚀 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=keyboard)
        return

    await message.answer(f"Assalomu alaykum, {message.from_user.first_name}!\nKerakli bo'limni tanlang:", reply_markup=get_main_menu())

@dp.callback_query_handler(text="check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    if await check_subscriptions(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer("Rahmat! Obuna tasdiqlandi. Kerakli bo'limni tanlang:", reply_markup=get_main_menu())
    else:
        await callback.answer("Siz hali hamma kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

# --- ADMIN PANEL ---

@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📚 Reading qo'shish", callback_data="adm_add_reading"),
        InlineKeyboardButton("✍️ Writing qo'shish", callback_data="adm_add_writing"),
        InlineKeyboardButton("🎧 Listening qo'shish", callback_data="adm_add_listening"),
        InlineKeyboardButton("🗣 Speaking qo'shish", callback_data="adm_add_speaking"),
        InlineKeyboardButton("❌ Chiqish", callback_data="adm_cancel")
    )
    await message.answer("🛠 **Admin panel:** Material qo'shmoqchi bo'lgan bo'limni tanlang:\n*(Eslatma: Fayl yuborganingizda unga izoh/caption yozishni unutmang!)*", reply_markup=keyboard)

@dp.callback_query_handler(text_startswith="adm_add_")
async def admin_select_section(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    section = callback.data.split("_")[2]
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📁 Fayl qo'shish", callback_data=f"type_file_{section}"),
        InlineKeyboardButton("🎬 Video qo'shish", callback_data=f"type_video_{section}"),
        InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_admin")
    )
    await callback.message.edit_text(f"📁 **{section.upper()}** bo'limiga nima qo'shmoqchisiz?", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query_handler(text_startswith="type_")
async def admin_choose_type(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    parts = callback.data.split("_")
    f_type = parts[1]
    section = parts[2]
    
    ADMIN_STATE[ADMIN_ID] = f"{section}_{f_type}"
    await callback.message.edit_text(f"✅ Siz **{section.upper()}** bo'limiga **{f_type.upper()}** tanladingiz.\n\nEndi menga o'sha fayl yoki videoni yuboring va **albatta izoh (caption)** yozib yuboring (masalan: Reading Part 5 - Muallif).")
    await callback.answer()

@dp.callback_query_handler(text="back_to_admin")
async def back_admin(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await cmd_admin(callback.message)
    await callback.message.delete()

@dp.callback_query_handler(text="adm_cancel")
async def cancel_admin(callback: types.CallbackQuery):
    ADMIN_STATE.pop(ADMIN_ID, None)
    await callback.message.delete()
    await callback.answer("Admin panel yopildi.")

# Admin material yuborganda uni caption (izoh) bilan saqlash
@dp.message_handler(content_types=[types.ContentType.DOCUMENT, types.ContentType.VIDEO, types.ContentType.AUDIO])
async def save_admin_material(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    
    state = ADMIN_STATE.get(ADMIN_ID)
    if not state: return
    
    section, f_type = state.split("_")
    caption = message.caption
    
    if not caption:
        await message.reply("⚠️ Xatolik! Iltimos, fayl yoki video bilan birga **izoh (caption)** ham yozib yuboring (Masalan: Reading Part 5).")
        return
    
    if message.content_type == types.ContentType.VIDEO and f_type == "video":
        file_id = message.video.file_id
        DATABASE[f"{section}_videos"].append({"file_id": file_id, "title": caption})
        await message.reply(f"✅ Video muvaffaqiyatli saqlandi!\nSarlavhasi: {caption}")
    elif message.content_type in [types.ContentType.DOCUMENT, types.ContentType.AUDIO] and f_type == "file":
        file_id = message.document.file_id if message.document else message.audio.file_id
        DATABASE[f"{section}_files"].append({"file_id": file_id, "title": caption})
        await message.reply(f"✅ Fayl muvaffaqiyatli saqlandi!\nSarlavhasi: {caption}")
    else:
        await message.reply(f"⚠️ Siz tanlagan turga mos kelmaydigan fayl yubordingiz.")

# --- FOYDALANUVCHI QISMI ---

@dp.callback_query_handler(text_startswith="main_")
async def user_select_main_menu(callback: types.CallbackQuery):
    section = callback.data.split("_")[1]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📁 Fayllar", callback_data=f"get_files_{section}"),
        InlineKeyboardButton("🎬 Videolar", callback_data=f"get_videos_{section}"),
        InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")
    )
    await callback.message.edit_text(f"📂 **{section.upper()}** bo'limi. Kerakli turini tanlang:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query_handler(text="back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("Assalomu alaykum! Kerakli bo'limni tanlang:", reply_markup=get_main_menu())
    await callback.answer()

# Ro'yxatni (tugmalarni) chiqarish
@dp.callback_query_handler(text_startswith="get_")
async def send_materials_list(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    m_type = parts[1] # files yoki videos
    section = parts[2] # reading...
    
    key = f"{section}_{m_type}"
    items = DATABASE.get(key, [])
    
    if not items:
        await callback.answer(f"📭 Hozircha bu bo'limda {m_type} mavjud emas!", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    # Har bir fayl uchun uning sarlavhasi (izohi) bilan tugma yaratamiz
    for index, item in enumerate(items):
        keyboard.add(InlineKeyboardButton(item["title"], callback_data=f"show_{section}_{m_type}_{index}"))
    
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"main_{section}"))
    
    await callback.message.edit_text(f"📋 **{section.upper()}** bo'limidagi {m_type} ro'yxati:\nKeraklisini tanlang:", reply_markup=keyboard)
    await callback.answer()

# Tanlangan bitta fayl yoki videoni yuborish
@dp.callback_query_handler(text_startswith="show_")
async def send_single_item(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    section = parts[1]
    m_type = parts[2]
    index = int(parts[3])
    
    key = f"{section}_{m_type}"
    items = DATABASE.get(key, [])
    
    if index < len(items):
        item = items[index]
        if m_type == "videos":
            await callback.message.answer_video(item["file_id"], caption=item["title"])
        else:
            await callback.message.answer_document(item["file_id"], caption=item["title"])
    else:
        await callback.answer("⚠️ Fayl topilmadi!", show_alert=True)
    await callback.answer()

# Biz bilan bog'lanish
@dp.callback_query_handler(text="contact_admin")
async def process_contact(callback: types.CallbackQuery):
    await callback.message.answer(f"📞 Admin bilan bog'lanish uchun: t.me/{ADMIN_USERNAME}\nSavollaringiz bo'lsa yozishingiz mumkin.")
    await callback.answer()

# About Me
@dp.callback_query_handler(text="about_me")
async def process_about(callback: types.CallbackQuery):
    await callback.message.answer("ℹ️ **About Me**\nUshbu bot ingliz tilini o'rganuvchilar uchun maxsus materiallar taqdim etish va 24/7 xizmat ko'rsatish uchun yaratilgan.")
    await callback.answer()

# Reklama kanallarini boshqarish
@dp.message_handler(commands=['addchan'])
async def add_channel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.get_args()
    if args and args not in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.append(args.strip())
        await message.reply(f"✅ {args} qo'shildi!")

@dp.message_handler(commands=['delchan'])
async def del_channel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.get_args()
    if args in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.remove(args.strip())
        await message.reply(f"🗑 {args} o'chirildi!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
