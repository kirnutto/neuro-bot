from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_student_main_kb, get_materials_inline_kb, get_main_inline_kb
from database import add_user, log_action
from data import COURSE_CURRICULUM
from ai_helper import get_ai_response

router = Router()

# ───────────────────────── ОНБОРДИНГ / СТАРТ ─────────────────────────

ONBOARDING_TEXT = (
    "Привет, {name}! 👋\n\n"
    "Я — *AI-Ментор* курса *«AIO: AI-видео с нуля до профи»*.\n"
    "Твой преподаватель: *Кирилл Орещенко*.\n\n"
    "Вот что ты можешь делать здесь:\n\n"
    "📚 *Материалы* — все 8 модулей курса с описанием уроков и домашними заданиями.\n"
    "❓ *Задать вопрос* — напиши любой вопрос по курсу, и я отвечу. Можно спрашивать несколько раз подряд, я помню контекст.\n"
    "📖 *О курсе* — что ты освоишь и какие инструменты будем использовать.\n"
    "✍️ *Написать Кириллу* — прямая связь с преподавателем.\n"
    "💡 *Помощь* — если что-то непонятно или нужна подсказка.\n\n"
    "С чего начнём? 🎬"
)

@router.message(Command("start"), StateFilter("*"))
@router.message(F.text == "🏠 Главное меню", StateFilter("*"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    user = message.from_user
    is_new = await add_user(user.id, user.username, user.first_name)
    await log_action(user.id, "started_bot")

    # Уведомить Кирилла о новом пользователе
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

    await message.answer(
        ONBOARDING_TEXT.format(name=user.first_name),
        parse_mode="Markdown",
        reply_markup=get_student_main_kb()
    )
    await message.answer(
        "Выбери, с чего начать 👇",
        reply_markup=get_main_inline_kb()
    )

# ───────────────────────── INLINE-КНОПКИ ГЛАВНОГО МЕНЮ ─────────────────────────

@router.callback_query(F.data == "menu_materials")
async def inline_materials(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Выбери модуль, который хочешь изучить 👇", reply_markup=get_materials_inline_kb())

@router.callback_query(F.data == "menu_ask")
async def inline_ask(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "🤖 Режим вопросов активирован!\n\n"
        "Спрашивай про курс, инструменты или работу с нейросетями. "
        "Я помню наш разговор, так что можешь задавать вопросы по цепочке.\n\n"
        "_Например:_\n"
        "— «С чего начать работу над мультфильмом?»\n"
        "— «Как составить промпт для Kling Motion?»\n\n"
        "Чтобы выйти — нажми *🏠 Главное меню*.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentState.waiting_for_question)

@router.callback_query(F.data == "menu_about")
async def inline_about(callback: CallbackQuery):
    await callback.answer()
    await about_course(callback.message)

@router.callback_query(F.data == "menu_contact")
async def inline_contact(callback: CallbackQuery):
    await callback.answer()
    await contact_kirill(callback.message)

@router.callback_query(F.data == "menu_help")
async def inline_help(callback: CallbackQuery):
    await callback.answer()
    await help_menu(callback.message)

# ───────────────────────── МАТЕРИАЛЫ ─────────────────────────

@router.message(F.text == "📚 Материалы")
async def materials_menu(message: Message):
    await log_action(message.from_user.id, "opened_materials")
    await message.answer(
        "Выбери модуль, который хочешь изучить 👇",
        reply_markup=get_materials_inline_kb()
    )

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

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

# ───────────────────────── О КУРСЕ ─────────────────────────

@router.message(F.text == "📖 О курсе")
async def about_course(message: Message):
    await log_action(message.from_user.id, "viewed_about")
    text = (
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
        "Всё обучение проходит *с телефона*, без сложных терминов и лишней теории. "
        "Только реальные проекты, которые можно сразу публиковать в соцсетях. 🚀"
    )
    await message.answer(text, parse_mode="Markdown")

# ───────────────────────── НАПИСАТЬ КИРИЛЛУ ─────────────────────────

@router.message(F.text == "✍️ Написать Кириллу")
async def contact_kirill(message: Message):
    await log_action(message.from_user.id, "contact_kirill")
    await message.answer(
        "Написать Кириллу напрямую можно здесь 👇\n\n"
        "➡️ @OrKIIg4781\n\n"
        "Он всегда на связи между занятиями 😊"
    )

# ───────────────────────── ПОМОЩЬ ─────────────────────────

@router.message(F.text == "💡 Помощь")
async def help_menu(message: Message):
    await log_action(message.from_user.id, "viewed_help")
    text = (
        "💡 *Как пользоваться ботом?*\n\n"
        "📚 *Материалы* — нажми и выбери нужный модуль. "
        "Там описание урока и домашнее задание.\n\n"
        "❓ *Задать вопрос* — нажми кнопку и просто напиши свой вопрос. "
        "Бот помнит всю переписку в рамках одного сеанса, поэтому можно задавать вопросы по цепочке.\n\n"
        "_Например:_\n"
        "— «Как создать паспорт персонажа?»\n"
        "— «А референс-лист — это что?»\n"
        "— «Дай пример промпта для Kling Motion»\n\n"
        "Чтобы выйти из режима вопросов — нажми *🏠 Главное меню*.\n\n"
        "📖 *О курсе* — краткое описание программы и инструментов.\n\n"
        "✍️ *Написать Кириллу* — прямая ссылка на преподавателя.\n\n"
        "Если бот завис или не отвечает — нажми *🏠 Главное меню* или отправь команду /start."
    )
    await message.answer(text, parse_mode="Markdown")

# ───────────────────────── AI-ЧАТ ─────────────────────────

class StudentState(StatesGroup):
    waiting_for_question = State()

MENU_BUTTONS = {"📚 Материалы", "❓ Задать вопрос", "📖 О курсе",
                "✍️ Написать Кириллу", "💡 Помощь", "🏠 Главное меню"}

@router.message(F.text == "❓ Задать вопрос")
async def ask_question_menu(message: Message, state: FSMContext):
    await log_action(message.from_user.id, "asked_question")
    await message.answer(
        "🤖 Режим вопросов активирован!\n\n"
        "Спрашивай про курс, инструменты или работу с нейросетями. "
        "Я помню наш разговор, так что можешь задавать вопросы по цепочке.\n\n"
        "_Например:_\n"
        "— «С чего начать работу над мультфильмом?»\n"
        "— «Как составить промпт для Kling Motion?»\n"
        "— «Как исправить деформацию рук на видео?»\n\n"
        "Чтобы выйти — нажми *🏠 Главное меню*.",
        parse_mode="Markdown"
    )
    await state.set_state(StudentState.waiting_for_question)

@router.message(StudentState.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    user_question = message.text

    # Если нажата кнопка меню — выходим из режима
    if user_question in MENU_BUTTONS:
        await state.clear()
        await message.answer("Возвращаемся в главное меню.", reply_markup=get_student_main_kb())
        return

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
    # Состояние НЕ сбрасываем — ученица может продолжать диалог
