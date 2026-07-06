import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.fsm.storage.memory import MemoryStorage

# ==========================
# НАСТРОЙКИ
# ==========================

BOT_TOKEN = "YOUR_BOT_TOKEN"
GROUP_ID = -1001234567890  # ID вашей группы

# ==========================
# ИНИЦИАЛИЗАЦИЯ
# ==========================

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# admin_id -> user_id
waiting_reply = {}

# ==========================
# START
# ==========================

@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        "👋 Привет! Напиши свой вопрос, я перешлю его руководству."
    )

# ==========================
# СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ
# ==========================

@dp.message(F.chat.type == "private")
async def user_message(message: Message):

    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "отсутствует"
    )

    text_value = (
        message.text
        if message.text
        else "отсутствует"
    )

    photo_value = (
        "есть"
        if message.photo
        else "отсутствует"
    )

    video_value = (
        "есть"
        if message.video
        else "отсутствует"
    )

    info_text = (
        f"📨 Новое обращение\n\n"
        f"👤 Username: {username}\n"
        f"🆔 ID: {user.id}\n\n"
        f"📝 Текст:\n{text_value}\n\n"
        f"📷 Фото: {photo_value}\n"
        f"🎥 Видео: {video_value}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ответить",
                    callback_data=f"reply_{user.id}"
                )
            ]
        ]
    )

    await bot.send_message(
        GROUP_ID,
        info_text,
        reply_markup=keyboard
    )

    if message.photo:
        await bot.send_photo(
            GROUP_ID,
            message.photo[-1].file_id,
            caption="Фото пользователя"
        )

    if message.video:
        await bot.send_video(
            GROUP_ID,
            message.video.file_id,
            caption="Видео пользователя"
        )

    await message.answer(
        "✅ Ваш вопрос отправлен руководству."
    )

# ==========================
# КНОПКА ОТВЕТИТЬ
# ==========================

@dp.callback_query(F.data.startswith("reply_"))
async def reply_button(callback: CallbackQuery):

    user_id = int(
        callback.data.replace("reply_", "")
    )

    admin_id = callback.from_user.id

    waiting_reply[admin_id] = user_id

    await callback.message.answer(
        f"✍ Теперь отправьте ответ пользователю ID {user_id}"
    )

    await callback.answer()

# ==========================
# ОТВЕТ АДМИНА ИЗ ГРУППЫ
# ==========================

@dp.message(F.chat.id == GROUP_ID)
async def admin_reply(message: Message):

    admin_id = message.from_user.id

    if admin_id not in waiting_reply:
        return

    user_id = waiting_reply[admin_id]

    text = message.text or ""

    await bot.send_message(
        user_id,
        f'Привет, вот ответ от руководства:\n\n"{text}"'
    )

    await message.reply(
        "✅ Ответ отправлен пользователю."
    )

    del waiting_reply[admin_id]

# ==========================
# ЗАПУСК
# ==========================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
