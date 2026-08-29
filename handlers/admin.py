from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_ID
from keyboards import get_admin_main_kb, get_student_main_kb
from database import get_all_users, get_user_stats

router = Router()

# Middleware-like filter for admin
def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message):
        return
    await message.answer("Добро пожаловать в панель администратора!", reply_markup=get_admin_main_kb())

@router.message(F.text == "📊 Статистика учеников")
async def stats_menu(message: Message):
    if not is_admin(message):
        return
    
    users = await get_all_users()
    if not users:
        await message.answer("Учеников пока нет.")
        return

    text = "Список учеников:\n"
    for u in users:
        text += f"- {u[1]} (ID: {u[0]})\n"
    
    # Just show stats for the first user for demo purposes
    first_user_id = users[0][0]
    stats = await get_user_stats(first_user_id)
    
    text += f"\nПоследние действия пользователя {first_user_id}:\n"
    for action, timestamp in stats:
        text += f"- {action} в {timestamp}\n"
        
    await message.answer(text)

@router.message(F.text == "📚 Режим ученика")
async def student_mode(message: Message):
    if not is_admin(message):
        return
    await message.answer("Переключаю в режим ученика.", reply_markup=get_student_main_kb())

@router.message(F.document)
async def get_document_id(message: Message):
    if not is_admin(message):
        return
    
    file_id = message.document.file_id
    file_name = message.document.file_name or "документ"
    await message.answer(
        f"✅ *Файл/документ получен:* `{file_name}`\n\n"
        f"📋 *File ID:*\n`{file_id}`\n\n"
        f"Отправь этот `file_id` ассистенту или вставь в `data.py` (для презентации или шпаргалки).",
        parse_mode="Markdown"
    )

@router.message(F.video)
async def get_video_id(message: Message):
    if not is_admin(message):
        return
    
    file_id = message.video.file_id
    await message.answer(
        f"✅ *Видео получено!*\n\n"
        f"📋 *File ID:*\n`{file_id}`\n\n"
        f"Отправь этот `file_id` ассистенту или вставь в `data.py` в поле `recording_video_id`.",
        parse_mode="Markdown"
    )

@router.message(F.photo)
async def get_photo_id(message: Message):
    if not is_admin(message):
        return
    
    file_id = message.photo[-1].file_id
    await message.answer(
        f"✅ *Фотография/изображение получено!*\n\n"
        f"📋 *File ID:*\n`{file_id}`",
        parse_mode="Markdown"
    )

