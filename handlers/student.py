from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_student_main_kb, get_materials_inline_kb, get_main_inline_kb, get_back_btn, get_module_back_kb
from database import add_user, log_action
from data import COURSE_CURRICULUM
from ai_helper import get_ai_response

router = Router()

# ───────────────────────── ОНБОРДИНГ / СТАРТ ─────────────────────────

ONBOARDING_TEXT = (
    "Привет, {name}! 👋\n\n"
    "Я — *AI-Ментор* курса *«AIO: AI-видео с нуля до профи»*.\n"
    "Твой преподаватель: *Кирилл Орещенко*.\n\n"
    "📚 *Материалы* — все 8 модулей курса\n"
    "❓ *Задать вопрос* — спроси что угодно по курсу\n"
    "📖 *О курсе* — программа и инструменты\n"
    "✍️ *Написать Кириллу* — прямая связь\n"
    "💡 *Помощь* — как пользоваться ботом\n\n"
    "👇 Выбери, с чего начать:"
)

class StudentState(StatesGroup):
    waiting_for_question = State()

MENU_BUTTONS = {"🏠 Главное меню"}

@router.message(Command("start"), StateFilter("*"))
@router.message(F.text == "🏠 Главное меню", StateFilter("*"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user = message.from_user
    is_new = await add_user(user.id, user.username, user.first_name)
    await log_action(user.id, "started_bot")

    # Notify admin about new user
    if is_new:
        from config import ADMIN_ID
        if ADMIN_ID:
            username_str = f"@{user.username}" if user.username else "без username"
            profile_link = f"tg://user?id={user.id}"
            await message.bot.send_message(
                ADMIN_ID,
                f"🆕 *Новый пользователь бота!*\n\n"
                f"👤 Имя: [{user.full_name}]({profile_link})\n"
                f"📎 Telegram: {username_str}\n"
                f"🆔 ID: `{user.id}`",
                parse_mode="Markdown"
            )

    # Delete user's message to keep chat clean
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer(
        ONBOARDING_TEXT.format(name=user.first_name),
        parse_mode="Markdown",
        reply_markup=get_main_inline_kb()
    )

# ───────────────────────── INLINE-КНОПКИ ГЛАВНОГО МЕНЮ ─────────────────────────

@router.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        ONBOARDING_TEXT.format(name=callback.from_user.first_name),
        parse_mode="Markdown",
        reply_markup=get_main_inline_kb()
    )

@router.callback_query(F.data == "menu_materials")
async def inline_materials(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📚 *Материалы курса*\n\nВыбери модуль, который хочешь изучить 👇",
        parse_mode="Markdown",
        reply_markup=get_materials_inline_kb()
    )

@router.callback_query(F.data == "menu_ask")
async def inline_ask(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "🤖 *Режим вопросов активирован!*\n\n"
        "Спрашивай про курс, инструменты или работу с нейросетями. "
        "Я помню весь наш разговор, так что можно задавать вопросы по цепочке.\n\n"
        "_Например:_\n"
        "— «С чего начать работу над мультфильмом?»\n"
        "— «Как составить промпт для Kling Motion?»\n"
        "— «Как исправить деформацию рук на видео?»\n\n"
        "Напиши свой вопрос прямо сейчас ✍️\n"
        "Чтобы выйти — нажми кнопку ниже 👇",
        parse_mode="Markdown",
        reply_markup=get_back_btn()
    )
    await state.set_state(StudentState.waiting_for_question)

@router.callback_query(F.data == "menu_about")
async def inline_about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🎬 *AIO: AI-видео с нуля до профи*\n\n"
        "Практический курс из *8 индивидуальных занятий* по 2 часа.\n\n"
        "После курса ты самостоятельно умеешь:\n"
        "✅ Создавать постоянных персонажей с нейросетью\n"
        "✅ Оживлять фотографии и персонажей\n"
        "✅ Делать AI-аватары для соцсетей\n"
        "✅ Создавать мультфильмы в разных стилях\n"
        "✅ Снимать реалистичные кино-сцены\n"
        "✅ Монтировать всё в готовый ролик\n\n"
        "🛠 *Инструменты курса:*\n"
        "• ChatGPT\n"
        "• Kling Motion\n"
        "• HeyGen\n"
        "• Seedance 2.5\n"
        "• Видеоредактор\n\n"
        "Всё обучение проходит *с телефона*, без сложных терминов. "
        "Только реальные проекты для соцсетей. 🚀",
        parse_mode="Markdown",
        reply_markup=get_back_btn()
    )

@router.callback_query(F.data == "menu_contact")
async def inline_contact(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "✍️ *Написать Кириллу напрямую:*\n\n"
        "➡️ @OrKIIg4781\n\n"
        "Он всегда на связи между занятиями 😊",
        parse_mode="Markdown",
        reply_markup=get_back_btn()
    )

@router.callback_query(F.data == "menu_help")
async def inline_help(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💡 *Как пользоваться ботом?*\n\n"
        "📚 *Материалы* — нажми и выбери нужный модуль. "
        "Там описание урока.\n\n"
        "❓ *Задать вопрос* — нажми и просто напиши вопрос. "
        "Бот помнит весь разговор, можно спрашивать по цепочке:\n"
        "_«Как создать паспорт персонажа?»_\n"
        "_«А референс-лист — это что?»_\n"
        "_«Дай пример промпта для Kling Motion»_\n\n"
        "📖 *О курсе* — описание программы и инструментов.\n\n"
        "✍️ *Написать Кириллу* — ссылка на преподавателя.\n\n"
        "Если бот завис — нажми *🏠 Главное меню* внизу или /start.",
        parse_mode="Markdown",
        reply_markup=get_back_btn()
    )

# ───────────────────────── МАТЕРИАЛЫ — МОДУЛИ ─────────────────────────

@router.callback_query(F.data.startswith("mod_"))
async def module_callback(callback: CallbackQuery):
    mod_id = callback.data
    await log_action(callback.from_user.id, f"viewed_module_{mod_id}")

    mod_data = COURSE_CURRICULUM.get(mod_id)
    if not mod_data:
        await callback.answer("Модуль не найден.")
        return

    text = f"📖 *{mod_data['title']}*\n\n"
    text += f"_{mod_data['description']}_\n\n"

    for lesson in mod_data["lessons"]:
        text += f"🔹 *{lesson['title']}*\n{lesson['content']}\n\n"

    # Telegram limit is 4096 chars — truncate if needed
    if len(text) > 4000:
        text = text[:3990] + "\n\n_...продолжение на занятии_ 📌"

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_module_back_kb()
    )
    await callback.answer()

# ───────────────────────── AI-ЧАТ ─────────────────────────

@router.message(F.text == "📚 Материалы")
async def materials_menu(message: Message):
    await log_action(message.from_user.id, "opened_materials")
    try:
        await message.delete()
    except Exception:
        pass
    await message.answer(
        "📚 *Материалы курса*\n\nВыбери модуль, который хочешь изучить 👇",
        parse_mode="Markdown",
        reply_markup=get_materials_inline_kb()
    )

@router.message(StudentState.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    user_question = message.text

    if user_question in MENU_BUTTONS:
        await state.clear()
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(
            ONBOARDING_TEXT.format(name=message.from_user.first_name),
            parse_mode="Markdown",
            reply_markup=get_main_inline_kb()
        )
        return

    # Delete user question to keep chat cleaner (optional, comment out if you prefer to keep)
    # await message.delete()

    processing_msg = await message.answer("🤖 Думаю над ответом...")

    ai_answer = await get_ai_response(user_question, message.from_user.first_name, message.from_user.id)

    if ai_answer.startswith("Произошла ошибка"):
        from config import ADMIN_ID
        if ADMIN_ID:
            await message.bot.send_message(
                ADMIN_ID,
                f"❓ Вопрос от {message.from_user.first_name} (@{message.from_user.username}):\n\n{user_question}"
            )
        await processing_msg.edit_text(
            "Произошла ошибка при обращении к нейросети. Я передал твой вопрос напрямую Кириллу!"
        )
    else:
        await processing_msg.edit_text(ai_answer, parse_mode="Markdown")

    await log_action(message.from_user.id, "received_ai_answer")
