from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import ensure_user, get_balance

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    balance = await get_balance(message.from_user.id)
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"💰 Твой баланс: <b>{balance}</b>\n\n"
        "🎮 <b>Игры:</b>\n"
        "• <code>краш [ставка]</code> или <code>кр [ставка]</code>\n"
        "• <code>21 [ставка]</code> / <code>бд [ставка]</code>\n"
        "• <code>кубы [ставка] [1-6]</code>\n"
        "• <code>дуэль [ставка]</code> (ответом на сообщение)\n"
        "• <code>казик [ставка]</code> / <code>казино [ставка]</code>\n"
        "• <code>боулинг [ставка] [1-6]</code>\n"
        "• <code>орел [ставка]</code> / <code>решка [ставка]</code>\n\n"
        "💸 <code>передать [сумма]</code> — перевод (ответом на сообщение)\n"
        "📜 <code>мои игры</code> — последние 40 игр\n"
        "💰 <code>баланс</code> — посмотреть баланс"
    )


@router.message(F.text.lower().in_({"баланс", "б", "balance"}))
async def cmd_balance(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    balance = await get_balance(message.from_user.id)
    await message.answer(f"💰 Твой баланс: <b>{balance}</b>")
