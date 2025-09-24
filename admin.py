from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import sqlite3
from config import TG_ADMIN_IDS
from database import get_user_limit_and_reset_date, update_user_limit_and_reset_date, get_total_users

router = Router()

# bot будет передаваться сюда как объект
async def set_bot_instance(bot_instance):
    global bot
    bot = bot_instance

@router.message(Command('add_zapros'))
async def admin_add_requests(message: Message):
    if message.from_user.id not in TG_ADMIN_IDS:
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("Используйте: /add_zapros <user_id> <count>")
        return

    try:
        target_user_id = int(args[1])
        count = int(args[2])
    except ValueError:
        await message.answer("ID и количество должны быть числами.")
        return

    current_limit, _ = get_user_limit_and_reset_date(target_user_id)
    new_limit = current_limit + count
    update_user_limit_and_reset_date(target_user_id, new_limit)

    await message.answer(f"Пользователю {target_user_id} добавлено {count} запросов. Всего: {new_limit}")

# Новая команда: /delet_zapros <user_id>
@router.message(Command('delet_zapros'))
async def admin_delete_requests(message: Message):
    if message.from_user.id not in TG_ADMIN_IDS:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте: /delet_zapros <user_id>")
        return

    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("ID должен быть числом.")
        return

    # Обнуляем лимит
    update_user_limit_and_reset_date(target_user_id, 0)

    await message.answer(f"У пользователя {target_user_id} все лимиты удалены (обнулён).")

@router.message(Command('call'))
async def admin_broadcast(message: Message):
    if message.from_user.id not in TG_ADMIN_IDS:
        return

    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.answer("Введите текст рассылки после команды /call")
        return

    broadcast_text = text[1]

    # Получим всех юзеров из БД
    conn = sqlite3.connect("mail_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    success = 0
    failed = 0

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, f"📢 <b>Новое сообщение от администратора:</b>\n\n{broadcast_text}")
            success += 1
        except Exception:
            failed += 1

    await message.answer(f"Рассылка завершена:\n✅ Успешно: {success}\n❌ Ошибок: {failed}")

@router.message(Command('stata'))
async def admin_stats(message: Message):
    if message.from_user.id not in TG_ADMIN_IDS:
        return

    total_users = get_total_users()
    await message.answer(f"📊 Всего пользователей в боте: {total_users}")