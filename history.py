from aiogram import Router, F
from aiogram.types import Message
from database import get_history, ensure_user

router = Router()


@router.message(F.text.lower().in_({
    "мои игры", "история", "лог", "my games"
}))
async def my_games(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    games = await get_history(message.from_user.id, 40)
    if not games:
        return await message.answer("📭 Игр пока нет")

    text = "📜 <b>Последние игры:</b>\n\n"
    for g in games:
        status = "✅ выиграл" if g["result"] == "win" else "❌ проиграл"
        line = f"• {g['game_type']} | ставка {g['bet']} → {status}"
        if g["win_amount"]:
            line += f" (+{g['win_amount']})"
        text += line + "\n"
    await message.answer(text)
