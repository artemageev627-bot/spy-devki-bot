import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F

TOKEN = "8520367789:AAEWveincfCFZ7KrSPPzfiY0TCNvzR6XIho"

bot = Bot(token=TOKEN)
dp = Dispatcher()

CHARACTERS = [
    "Арина Дементьева", "Алина Андриянова", "Руся", "Де линт",
    "Арина Бетхер", "Дуся", "Шутова", "Изобэйнал",
    "Елена Максимовна", "Марина Юрьевна", "Наташа Москвина",
    "Анжелика", "Михеева", "Игошина", "Марина", "Даша",
    "Тамара", "Шилова", "Татьяна Геннадьевна", "Муравьева",
    "Хасанова", "Алина Кузнецова"
]

games = {}

def players_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{i} игроков", callback_data=f"players_{i}")]
        for i in range(3, 8)
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎮 Игра «Шпион»\n\nВыбери количество игроков:",
        reply_markup=players_keyboard()
    )

@dp.callback_query(F.data.startswith("players_"))
async def set_players(callback: types.CallbackQuery):
    await callback.answer()
    count = int(callback.data.split("_")[1])
    games[callback.message.chat.id] = {"players_count": count, "players": []}

    await callback.message.answer(
        f"👥 Игроков: {count}\n\nНажмите «Я игрок»",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🙋 Я игрок", callback_data="join")]
        ])
    )

@dp.callback_query(F.data == "join")
async def join_game(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    uid = callback.from_user.id
    game = games.get(chat_id)

    if not game:
        return

    if uid not in game["players"]:
        game["players"].append(uid)
        await callback.message.answer("✅ Ты в игре")

    if len(game["players"]) == game["players_count"]:
        await start_game(chat_id)

async def start_game(chat_id):
    players = games[chat_id]["players"]
    spy = random.choice(players)
    character = random.choice(CHARACTERS)

    for uid in players:
        if uid == spy:
            text = "🕵️ Ты — ШПИОН"
        else:
            text = f"🎭 Персонаж: **{character}**"
        await bot.send_message(uid, text, parse_mode="Markdown")

    await bot.send_message(chat_id, "🎲 Игра началась!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
