from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Начать рассылку📩', callback_data='start_sms'),
        InlineKeyboardButton(text='Профиль🥷', callback_data='profil')
    ],
    
    [InlineKeyboardButton(text='Тех.поддержка👨🏻‍💻', url='https://t.me/TheRYXION')],
    [InlineKeyboardButton(text='FAQ', callback_data='faq_sms')],
    
])


rass_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить Gmail-аккаунт', callback_data='add_gmail')
    ]
])