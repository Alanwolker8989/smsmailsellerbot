from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import keyboard as kb

router = Router()

#Начало
@router.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(f"""
<b>Здравствуйте, {message.from_user.first_name}! 👋</b>\n
Добро пожаловать в наш сервис <b>email-рассылок</b>. ✉️\n
Мы создали платформу, которая помогает <i>легко и быстро</i> общаться с вашей аудиторией прямо из аккаунта Google.\n
<b>Просто</b>, <b>удобно</b> и <b>эффективно</b> — всё, чтобы ваши письма доходили до адресатов и работали на результат. 🚀
""",reply_markup=kb.menu_kb,parse_mode="HTML")

#Обработка кнопки FAQ
@router.callback_query(F.data == 'start_sms')
async def choose_sms_mode(callback: CallbackQuery):
    # Отправляем сообщение с выбором режима рассылки
    await callback.message.answer(
        text="Выберите режим рассылки:",
        reply_markup=kb.rass_kb
    )
    await callback.answer()
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
Да, всё происходит через безопасное протоколы.
"""    
@router.callback_query(F.data == 'faq_sms')
async def show_faq(callback: CallbackQuery):
    await callback.message.answer(faq_text, parse_mode="HTML")
    await callback.answer()   
     
#Обработка кнопки профиль
@router.callback_query(F.data == 'profil')
async def show_profile(callback: CallbackQuery):
    user = callback.from_user
    subscription_status = "Бесплатный"  
    profile_text = f"""
<b>👤 Ваш профиль:</b>

<b>Имя:</b> {user.first_name} {user.last_name or ''}
<b>ID:</b> {user.id}
<b>Подписка:</b> {subscription_status}
"""
    await callback.message.edit_text(profile_text, parse_mode="HTML")
    await callback.answer()

