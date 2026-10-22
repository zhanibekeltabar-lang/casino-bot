from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import (
    is_admin, change_balance, set_balance, set_admin,
    get_balance, ensure_user, set_no_limit
)
from config import MAIN_ADMIN_ID

router = Router()


def is_main_admin(user_id: int) -> bool:
    return user_id == MAIN_ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_main_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 <b>Админ-панель</b> (только для тебя)\n\n"
        "/give [user_id] [сумма] — выдать валюту (без лимита)\n"
        "/take [user_id] [сумма] — забрать валюту\n"
        "/setbal [user_id] [сумма] — установить баланс\n"
        "/makeadmin [user_id] — выдать админку\n"
        "/deladmin [user_id] — забрать админку\n"
        "/bal [user_id] — посмотреть баланс\n"
        "/nolimit [user_id] — снять лимит переводов (сделать безлимит)\n"
        "/limit [user_id] — вернуть лимит переводов\n\n"
        "⚠️ Эти команды видит и может использовать только главный админ."
    )


@router.message(Command("give"))
async def give_money(message: Message):
    if not await is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        uid = int(parts[1])
        amount = int(parts[2])  # Python поддерживает очень большие числа
        await ensure_user(uid)
        await change_balance(uid, amount)
        await message.answer(f"✅ Пользователю {uid} выдано <b>{amount}</b>")
    except Exception:
        await message.answer("Формат: /give [user_id] [сумма]")


@router.message(Command("take"))
async def take_money(message: Message):
    if not await is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        uid = int(parts[1])
        amount = int(parts[2])
        success = await change_balance(uid, -amount)
        if success:
            await message.answer(f"✅ У пользователя {uid} забрано <b>{amount}</b>")
        else:
            await message.answer("❌ Недостаточно средств или пользователь не найден")
    except Exception:
        await message.answer("Формат: /take [user_id] [сумма]")


@router.message(Command("setbal"))
async def set_bal(message: Message):
    if not await is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        uid = int(parts[1])
        amount = int(parts[2])
        await ensure_user(uid)
        await set_balance(uid, amount)
        await message.answer(f"✅ Баланс {uid} установлен на <b>{amount}</b>")
    except Exception:
        await message.answer("Формат: /setbal [user_id] [сумма]")


@router.message(Command("makeadmin"))
async def make_admin(message: Message):
    if not is_main_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.split()[1])
        await ensure_user(uid)
        await set_admin(uid, 1)
        await message.answer(
            f"✅ {uid} теперь админ.\n"
            f"Он может использовать /give, /take, /setbal, /bal.\n"
            f"Команды /admin, /makeadmin, /deladmin, /nolimit доступны только тебе."
        )
    except Exception:
        await message.answer("Формат: /makeadmin [user_id]")


@router.message(Command("deladmin"))
async def del_admin(message: Message):
    if not is_main_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.split()[1])
        await set_admin(uid, 0)
        await message.answer(f"✅ У {uid} забрана админка")
    except Exception:
        await message.answer("Формат: /deladmin [user_id]")


@router.message(Command("bal"))
async def check_bal(message: Message):
    if not await is_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.split()[1])
        bal = await get_balance(uid)
        await message.answer(f"💰 Баланс {uid}: <b>{bal}</b>")
    except Exception:
        await message.answer("Формат: /bal [user_id]")


@router.message(Command("nolimit"))
async def give_nolimit(message: Message):
    if not is_main_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.split()[1])
        await ensure_user(uid)
        await set_no_limit(uid, 1)
        await message.answer(f"✅ Пользователю {uid} снят лимит переводов (теперь безлимит)")
    except Exception:
        await message.answer("Формат: /nolimit [user_id]")


@router.message(Command("limit"))
async def return_limit(message: Message):
    if not is_main_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.split()[1])
        await set_no_limit(uid, 0)
        await message.answer(f"✅ Пользователю {uid} возвращён лимит переводов (1 млрд)")
    except Exception:
        await message.answer("Формат: /limit [user_id]")
