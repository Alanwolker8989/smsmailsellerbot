from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import keyboard as kb
from database import (
    save_user,
    get_user_limit,
    update_user_limit,
    update_user_gmail_password,
    get_user_gmail_password
)
from mail_sender import send_email_smtp

router = Router()

class MailStates(StatesGroup):
    waiting_gmail = State()
    waiting_password = State()
    waiting_body = State()
    waiting_recipients = State()

#Начало
@router.message(CommandStart())
async def start_cmd(message: Message):
    user = message.from_user
    save_user(user.id, user.username or f"user_{user.id}")
    await message.answer(f"""
<b>Здравствуйте, {message.from_user.first_name}! 👋</b>\n
Добро пожаловать в наш сервис <b>email-рассылок</b>. ✉️\n
Мы создали платформу, которая помогает <i>легко и быстро</i> общаться с вашей аудиторией прямо из аккаунта Google.\n
<b>Просто</b>, <b>удобно</b> и <b>эффективно</b> — всё, чтобы ваши письма доходили до адресатов и работали на результат. 🚀
""",reply_markup=kb.menu_kb,parse_mode="HTML")

#Обработка кнопки FAQ
@router.callback_query(F.data == 'start_sms')
async def choose_sms_mode(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    gmail, password = get_user_gmail_password(user_id)

    if gmail and password:
        await callback.message.answer(f"Вы авторизованы как: {gmail}\nВведите текст письма:")
        await state.set_state(MailStates.waiting_body)
    else:
        await callback.message.answer("Добавьте Gmail-аккаунт:", reply_markup=kb.rass_kb)
    await callback.answer()

@router.callback_query(F.data == 'add_gmail')
async def prompt_gmail(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваш Gmail-адрес (с которого будет рассылка):")
    await state.set_state(MailStates.waiting_gmail)
    await callback.answer()

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

    await message.answer(f"✅ Gmail-аккаунт {email} добавлен!\nВведите текст письма:")
    await state.set_state(MailStates.waiting_body)

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
    current_limit = get_user_limit(user_id)
    if current_limit <= 0:
        await message.answer("❌ Лимит рассылок исчерпан.")
        await state.clear()
        return

    # Уменьшаем лимит
    update_user_limit(user_id, current_limit - 1)

    # Отправляем
    for recipient in recipients:
        success = send_email_smtp(gmail, password, recipient, "Рассылка", body)
        if not success:
            await message.answer(f"❌ Ошибка при отправке на {recipient}")
            break
    else:
        await message.answer(f"✅ Письма отправлены на: {', '.join(recipients)}")

    await state.clear()

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
     
#Обработка кнопки профиль
@router.callback_query(F.data == 'profil')
async def show_profile(callback: CallbackQuery):
    user = callback.from_user 
    limit_user = get_user_limit(user.id)
    profile_text = f"""
<b>👤 Ваш профиль:</b>

<b>Имя:</b> {user.first_name} {user.last_name or ''}
<b>ID:</b> {user.id}
<b>Мои лимиты:</b> {limit_user}
"""
    await callback.message.edit_text(profile_text, parse_mode="HTML")
    await callback.answer()