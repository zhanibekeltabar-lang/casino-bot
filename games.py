import random
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    ensure_user, change_balance, add_history,
    has_no_limit, DEFAULT_TRANSFER_LIMIT
)
from config import MIN_BET, MAX_BET

router = Router()

active_crashes = {}
pending_duels = {}


def bet_ok(amount: int) -> bool:
    return amount >= MIN_BET


# ==================== КУБЫ (официальный 🎲) ====================
@router.message(F.text.regexp(r"(?i)^кубы\s+(\d+)\s+([1-6])$"))
async def dice_game(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    _, bet_str, number_str = message.text.split()
    bet, number = int(bet_str), int(number_str)

    if not bet_ok(bet):
        return await message.answer(f"Ставка должна быть от {MIN_BET}")

    if not await change_balance(message.from_user.id, -bet):
        return await message.answer("❌ Недостаточно средств")

    dice_msg = await message.answer_dice(emoji="🎲")
    await asyncio.sleep(3.5)

    value = dice_msg.dice.value

    if value == number:
        win = bet * 12
        await change_balance(message.from_user.id, win)
        await add_history(message.from_user.id, "Кубы", bet, "win", win)
        await message.answer(f"🎲 Выпало: <b>{value}</b>\n✅ Ты угадал! ×12 → +{win}")
    else:
        await add_history(message.from_user.id, "Кубы", bet, "lose")
        await message.answer(f"🎲 Выпало: <b>{value}</b>\n❌ Не угадал")


# ==================== ПЕРЕВОД ДЕНЕГ ====================
@router.message(F.text.regexp(r"(?i)^(передать|перевод)\s+(\d+)$"), F.reply_to_message)
async def transfer_money(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    to_user = message.reply_to_message.from_user

    if to_user.id == message.from_user.id:
        return await message.answer("Нельзя перевести самому себе")
    if to_user.is_bot:
        return await message.answer("Нельзя переводить боту")

    amount = int(message.text.split()[1])
    if amount <= 0:
        return await message.answer("Сумма должна быть больше 0")

    no_limit = await has_no_limit(message.from_user.id)
    if not no_limit and amount > DEFAULT_TRANSFER_LIMIT:
        return await message.answer(
            f"❌ Лимит перевода — {DEFAULT_TRANSFER_LIMIT:,}\n"
            f"Чтобы снять лимит — купи право у администратора."
        )

    if not await change_balance(message.from_user.id, -amount):
        return await message.answer("❌ Недостаточно средств")

    await ensure_user(to_user.id, to_user.username)
    await change_balance(to_user.id, amount)

    await message.answer(f"✅ Переведено <b>{amount}</b> пользователю {to_user.first_name}")
    try:
        await message.bot.send_message(
            to_user.id,
            f"💰 Тебе перевели <b>{amount}</b> от {message.from_user.first_name}"
        )
    except Exception:
        pass


# ==================== ОРЁЛ / РЕШКА ====================
@router.message(F.text.regexp(r"(?i)^(орел|решка)\s+(\d+)$"))
async def coinflip(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    choice, bet_str = message.text.lower().split()
    bet = int(bet_str)
    if not bet_ok(bet):
        return await message.answer(f"Ставка должна быть от {MIN_BET}")

    if not await change_balance(message.from_user.id, -bet):
        return await message.answer("❌ Недостаточно средств")

    result = random.choice(["орел", "решка"])
    if choice == result:
        win = bet * 2
        await change_balance(message.from_user.id, win)
        await add_history(message.from_user.id, "Орел/Решка", bet, "win", win)
        await message.answer(f"🪙 Выпало: <b>{result}</b>\n✅ Победа! +{win}")
    else:
        await add_history(message.from_user.id, "Орел/Решка", bet, "lose")
        await message.answer(f"🪙 Выпало: <b>{result}</b>\n❌ Проигрыш")


# ==================== БОУЛИНГ ====================
@router.message(F.text.regexp(r"(?i)^(кегля|кегли|боулинг)\s+(\d+)\s+([1-6])$"))
async def bowling(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    parts = message.text.lower().split()
    bet, number = int(parts[1]), int(parts[2])
    if not bet_ok(bet):
        return await message.answer(f"Ставка должна быть от {MIN_BET}")

    if not await change_balance(message.from_user.id, -bet):
        return await message.answer("❌ Недостаточно средств")

    bowl_msg = await message.answer_dice(emoji="🎳")
    await asyncio.sleep(4)
    value = bowl_msg.dice.value

    if value == number:
        win = bet * 10
        await change_balance(message.from_user.id, win)
        await add_history(message.from_user.id, "Боулинг", bet, "win", win)
        await message.answer(f"🎳 Выпало: <b>{value}</b>\n✅ Угадал! ×10 → +{win}")
    else:
        await add_history(message.from_user.id, "Боулинг", bet, "lose")
        await message.answer(f"🎳 Выпало: <b>{value}</b>\n❌ Не угадал")


# ==================== КАЗИНО ====================
@router.message(F.text.regexp(r"(?i)^(казик|казино)\s+(\d+)$"))
async def casino(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    bet = int(message.text.split()[1])
    if not bet_ok(bet):
        return await message.answer(f"Ставка должна быть от {MIN_BET}")

    if not await change_balance(message.from_user.id, -bet):
        return await message.answer("❌ Недостаточно средств")

    symbols = ["🍋", "🍒", "🍊", "7️⃣", "💎", "🔔"]
    reel = [random.choice(symbols) for _ in range(3)]
    result_text = " | ".join(reel)

    if reel.count("7️⃣") == 3:
        mult = 50
    elif reel.count("🍋") == 3:
        mult = 25
    elif len(set(reel)) == 1:
        mult = 10
    elif reel[0] == reel[1] or reel[1] == reel[2] or reel[0] == reel[2]:
        mult = 2
    else:
        mult = 0

    if mult:
        win = bet * mult
        await change_balance(message.from_user.id, win)
        await add_history(message.from_user.id, "Казино", bet, "win", win)
        await message.answer(f"🎰 {result_text}\n✅ Победа! ×{mult} → +{win}")
    else:
        await add_history(message.from_user.id, "Казино", bet, "lose")
        await message.answer(f"🎰 {result_text}\n❌ Проигрыш")


# ==================== ДУЭЛЬ ====================
@router.message(F.text.regexp(r"(?i)^дуэль\s+(\d+)$"), F.reply_to_message)
async def duel_start(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    opponent = message.reply_to_message.from_user

    if opponent.id == message.from_user.id:
        return await message.answer("Нельзя вызвать себя на дуэль")
    if opponent.is_bot:
        return await message.answer("Нельзя вызвать бота")

    bet = int(message.text.split()[1])
    if not bet_ok(bet):
        return await message.answer(f"Ставка должна быть от {MIN_BET}")

    if not await change_balance(message.from_user.id, -bet):
        return await message.answer("❌ Недостаточно средств")

    pending_duels[message.from_user.id] = (opponent.id, bet)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"duel_accept:{message.from_user.id}:{bet}"),
            InlineKeyboardButton(text="❌ Отказаться", callback_data=f"duel_decline:{message.from_user.id}")
        ]
    ])
    await message.answer(
        f"⚔️ <b>{message.from_user.first_name}</b> вызывает <b>{opponent.first_name}</b> на дуэль!\n"
        f"Ставка: <b>{bet}</b>\n\nПринимаешь?",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("duel_accept:"))
async def duel_accept(callback: CallbackQuery):
    _, challenger_id, bet = callback.data.split(":")
    challenger_id, bet = int(challenger_id), int(bet)
    accepter_id = callback.from_user.id

    if challenger_id not in pending_duels:
        return await callback.answer("Дуэль устарела", show_alert=True)
    if accepter_id != pending_duels[challenger_id][0]:
        return await callback.answer("Это не твоя дуэль", show_alert=True)

    if not await change_balance(accepter_id, -bet):
        await change_balance(challenger_id, bet)
        del pending_duels[challenger_id]
        return await callback.message.edit_text("❌ У принимающего недостаточно средств. Ставка возвращена.")

    winner = random.choice([challenger_id, accepter_id])
    loser = accepter_id if winner == challenger_id else challenger_id
    win_amount = bet * 2

    await change_balance(winner, win_amount)
    await add_history(winner, "Дуэль", bet, "win", win_amount)
    await add_history(loser, "Дуэль", bet, "lose")

    del pending_duels[challenger_id]
    await callback.message.edit_text(
        f"⚔️ Дуэль завершена!\n\n"
        f"🏆 Победитель ID: <code>{winner}</code>\n"
        f"Выигрыш: <b>{win_amount}</b>"
    )


@router.callback_query(F.data.startswith("duel_decline:"))
async def duel_decline(callback: CallbackQuery):
    challenger_id = int(callback.data.split(":")[1])
    if challenger_id not in pending_duels:
        return await callback.answer("Дуэль устарела", show_alert=True)
    if callback.from_user.id != pending_duels[challenger_id][0]:
        return await callback.answer("Это не твоя дуэль", show_alert=True)

    bet = pending_duels[challenger_id][1]
    await change_balance(challenger_id, bet)
    del pending_duels[challenger_id]
    await callback.message.edit_text("❌ Дуэль отклонена. Ставка возвращена.")


# ==================== КРАШ ====================
@router.message(F.text.regexp(r"(?i)^(краш|кр)\s+(\d+)$"))
async def crash_start(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    bet = int(message.text.split()[1])
    if not bet_ok(bet):
        return await message.answer(f"Ставка должна быть от {MIN_BET}")

    if message.from_user.id in active_crashes:
        return await message.answer("У тебя уже есть активный краш")

    if not await change_balance(message.from_user.id, -bet):
        return await message.answer("❌ Недостаточно средств")

    crash_point = round(min(random.expovariate(0.5) + 1.0, 20.0), 2)
    if crash_point < 1.1:
        crash_point = round(random.uniform(1.1, 2.5), 2)

    active_crashes[message.from_user.id] = {
        "bet": bet,
        "crash_point": crash_point,
        "current": 1.00,
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Забрать", callback_data=f"crash_cashout:{message.from_user.id}")]
    ])
    msg = await message.answer(
        f"🚀 <b>Краш начался!</b>\nСтавка: <b>{bet}</b>\nМножитель: <b>x1.00</b>",
        reply_markup=kb
    )
    active_crashes[message.from_user.id]["msg"] = msg

    current = 1.00
    while current < crash_point:
        await asyncio.sleep(0.65)
        if message.from_user.id not in active_crashes:
            return
        current = round(current + random.uniform(0.07, 0.28), 2)
        if current >= crash_point:
            break
        active_crashes[message.from_user.id]["current"] = current
        try:
            await msg.edit_text(
                f"🚀 <b>Краш!</b>\nСтавка: <b>{bet}</b>\nМножитель: <b>x{current:.2f}</b>",
                reply_markup=kb
            )
        except Exception:
            pass

    if message.from_user.id in active_crashes:
        del active_crashes[message.from_user.id]
        await add_history(message.from_user.id, "Краш", bet, "lose")
        try:
            await msg.edit_text(f"💥 Ракета взорвалась на <b>x{crash_point:.2f}</b>\n❌ Проигрыш")
        except Exception:
            pass


@router.callback_query(F.data.startswith("crash_cashout:"))
async def crash_cashout(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    if callback.from_user.id != user_id:
        return await callback.answer("Это не твоя игра", show_alert=True)
    if user_id not in active_crashes:
        return await callback.answer("Игра уже закончена", show_alert=True)

    data = active_crashes.pop(user_id)
    win = int(data["bet"] * data["current"])
    await change_balance(user_id, win)
    await add_history(user_id, "Краш", data["bet"], "win", win)
    await callback.message.edit_text(
        f"💸 Забрал на <b>x{data['current']:.2f}</b>\n✅ Выигрыш: <b>+{win}</b>"
    )


# ==================== 21 ОЧКО ====================
@router.message(F.text.regexp(r"(?i)^(21|бд|блекджек)\s+(\d+)$"))
async def blackjack(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    bet = int(message.text.split()[1])
    if not bet_ok(bet):
        return await message.answer(f"Ставка должна быть от {MIN_BET}")

    if not await change_balance(message.from_user.id, -bet):
        return await message.answer("❌ Недостаточно средств")

    player = random.randint(12, 21)
    dealer = random.randint(16, 24)

    if player > 21:
        result, win, text = "lose", 0, f"🃏 Твои очки: {player}\nДилер: {dealer}\n❌ Перебор! Проигрыш"
    elif dealer > 21 or player > dealer:
        win = bet * 2
        await change_balance(message.from_user.id, win)
        result, text = "win", f"🃏 Твои очки: {player}\nДилер: {dealer}\n✅ Победа! +{win}"
    elif player == dealer:
        win = bet
        await change_balance(message.from_user.id, win)
        result, text = "win", f"🃏 Твои очки: {player}\nДилер: {dealer}\n🤝 Ничья, ставка возвращена"
    else:
        result, win, text = "lose", 0, f"🃏 Твои очки: {player}\nДилер: {dealer}\n❌ Проигрыш"

    await add_history(message.from_user.id, "21", bet, result, win)
    await message.answer(text)
