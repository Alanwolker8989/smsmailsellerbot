from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import keyboard as kb
from database import (
    save_user,
    get_user_limit_and_reset_date,
    update_user_limit_and_reset_date,
    update_user_gmail_password,
    get_user_gmail_password,
    delete_user_gmail
)
from mail_sender import send_email_smtp
from config import TG_ADMIN_IDS

router = Router()

class MailStates(StatesGroup):
    waiting_gmail = State()
    waiting_password = State()
    waiting_body = State()
    waiting_recipients = State()

# Команда /start
@router.message(CommandStart())
async def start_cmd(message: Message):
    user = message.from_user
    save_user(user.id, user.username or f"user_{user.id}")
    await message.answer(f"""
<b>Здравствуйте, {message.from_user.first_name}! 👋</b>\n
Добро пожаловать в наш сервис <b>email-рассылок</b>. ✉️\n
Мы создали платформу, которая помогает <i>легко и быстро</i> общаться с вашей аудиторией прямо из аккаунта Google.\n
<b>Просто</b>, <b>удобно</b> и <b>эффективно</b> — всё, чтобы ваши письма доходили до адресатов и работали на результат. 🚀\n\n

<b>📋 Доступные команды:</b>
• <code>/add_akk</code> — добавить Gmail-аккаунт для рассылки
• <code>/delet_akk email@gmail.com</code> — удалить добавленный аккаунт

⚠️ <b>Бот находится в бета-тестировании!</b>
Во время использования могут возникать баги — сообщайте о них в <b>техподдержку</b>, если что-то пошло не так или у вас есть идеи, как улучшить бота — мы будем рады! 🙌

Для начала работы добавьте аккаунт и наслаждайтесь рассылкой!
""", reply_markup=kb.menu_kb, parse_mode="HTML")

# Команда /add_akk
@router.message(Command('add_akk'))
async def add_account_cmd(message: Message, state: FSMContext):
    if message.from_user.id in TG_ADMIN_IDS:
        await message.answer("Вы админ, используйте админ-команды.")
        return

    gmail, password = get_user_gmail_password(message.from_user.id)
    if gmail:
        await message.answer(f"У вас уже есть аккаунт: {gmail}\nЧтобы добавить новый — сначала удалите старый командой /delet_akk email@gmail.com")
        return

    await message.answer("Введите ваш Gmail-адрес (с которого будет рассылка):")
    await state.set_state(MailStates.waiting_gmail)

@router.message(MailStates.waiting_gmail)
async def prompt_password(message: Message, state: FSMContext):
    email = message.text.strip()

    if not email.endswith('@gmail.com'):
        await message.answer("Пожалуйста, введите корректный Gmail-адрес.")
        return

    await state.update_data(gmail=email)
    await message.answer("Введите пароль приложения Gmail (его можно получить в настройках Google):")
    await state.set_state(MailStates.waiting_password)

@router.message(MailStates.waiting_password)
async def save_gmail_and_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    email = data.get("gmail")

    update_user_gmail_password(message.from_user.id, email, password)

    await message.answer(f"✅ Gmail-аккаунт {email} добавлен!")
    await state.clear()

# Команда /delet_akk
@router.message(Command('delet_akk'))
async def delete_account_cmd(message: Message):
    if message.from_user.id in TG_ADMIN_IDS:
        await message.answer("Вы админ, используйте админ-команды.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте: /delet_akk email@gmail.com")
        return

    email = args[1]
    user_id = message.from_user.id

    current_email, _ = get_user_gmail_password(user_id)
    if current_email == email:
        delete_user_gmail(user_id)
        await message.answer(f"Аккаунт {email} успешно удалён.")
    else:
        await message.answer("У вас нет такого аккаунта.")

# Обработка кнопки "Начать рассылку"
@router.callback_query(F.data == 'start_sms')
async def choose_sms_mode(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    gmail, password = get_user_gmail_password(user_id)

    if not gmail or not password:
        await callback.message.answer("У вас нет добавленного аккаунта. Добавьте его командой /add_akk")
        await callback.answer()
        return

    await callback.message.answer(f"Вы авторизованы как: {gmail}\nВведите текст письма:")
    await state.set_state(MailStates.waiting_body)
    await callback.answer()

@router.message(MailStates.waiting_body)
async def get_body_and_ask_recipients(message: Message, state: FSMContext):
    await state.update_data(body=message.text)
    await message.answer("Введите email(ы) получателей (через запятую, если несколько):")
    await state.set_state(MailStates.waiting_recipients)

@router.message(MailStates.waiting_recipients)
async def get_recipients_and_send(message: Message, state: FSMContext):
    recipients_text = message.text.strip()
    recipients = [r.strip() for r in recipients_text.split(",") if r.strip()]

    data = await state.get_data()
    body = data.get("body")
    user_id = message.from_user.id
    gmail, password = get_user_gmail_password(user_id)

    if not gmail or not password:
        await message.answer("❌ Ошибка: нет сохранённых данных для отправки.")
        await state.clear()
        return

    # Проверка лимита
    current_limit, last_reset = get_user_limit_and_reset_date(user_id)
    if current_limit <= 0:
        # Проверим, прошло ли 24 часа с last_reset
        last_reset_time = datetime.fromisoformat(last_reset)
        if datetime.now() < last_reset_time + timedelta(hours=24):
            await message.answer("❌ Лимит рассылок исчерпан. Попробуйте позже.")
            await state.clear()
            return
        else:
            # Прошло 24 часа — сбрасываем
            update_user_limit_and_reset_date(user_id, 5)
            current_limit = 5

    # Уменьшаем лимит
    update_user_limit_and_reset_date(user_id, current_limit - 1)

    # Отправляем
    for recipient in recipients:
        success = send_email_smtp(gmail, password, recipient, "Рассылка", body)
        if not success:
            await message.answer(f"❌ Ошибка при отправке на {recipient}")
            await state.clear()
            return

    await message.answer(f"✅ Письма отправлены на: {', '.join(recipients)}\n\nВозвращаюсь к главному меню.", reply_markup=kb.menu_kb)
    await state.clear()

# FAQ
faq_text = """
<b>❓Ответ на вопросы:</b>

<b>1. Зачем нужен бесплатный режим?</b>
Чтобы попробовать сервис без вложений. В бесплатном режиме — 5 запросов на рассылку в день.

<b>2. Чем платный режим лучше?</b>
• Неограниченная рассылка
• Приоритетная поддержка
• Высокая скорость доставки

<b>3. Можно ли перейти с бесплатного на платный?</b>
Да, в любой момент как вам станет необходимо.

<b>4. Безопасно ли это?</b>
Да, всё происходит через безопасные протоколы.
"""

@router.callback_query(F.data == 'faq_sms')
async def show_faq(callback: CallbackQuery):
    await callback.message.answer(faq_text, parse_mode="HTML")
    await callback.answer()

# Профиль
@router.callback_query(F.data == 'profil')
async def show_profile(callback: CallbackQuery):
    user = callback.from_user
    limit_user, last_reset = get_user_limit_and_reset_date(user.id)

    last_reset_time = datetime.fromisoformat(last_reset)
    next_reset_time = last_reset_time + timedelta(hours=24)
    time_left = next_reset_time - datetime.now()

    if time_left.total_seconds() <= 0:
        time_left_str = "Готово"
    else:
        hours, remainder = divmod(int(time_left.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    profile_text = f"""
<b>👤 Ваш профиль:</b>

<b>Имя:</b> {user.first_name} {user.last_name or ''}
<b>ID:</b> {user.id}
<b>Мои лимиты:</b> {limit_user}
"""
    if limit_user <= 0:
        profile_text += f"\n<b>Следующее восстановление лимитов:</b> {time_left_str}"

    await callback.message.edit_text(profile_text, parse_mode="HTML")
    await callback.answer()