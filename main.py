import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8520367789:AAEWveincfCFZ7KrSPPzfiY0TCNvzR6XIho"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

characters = [
    "Арина Дементьева", "Алина Андриянова", "Руся", "Де линт", "Арина Бетхер",
    "Дуся", "Шутова", "Изобэйнал", "Елена Максимовна", "Марина Юрьевна",
    "Наташа Москвина", "Анжелика", "Михеева", "Игошина", "Марина", "Даша",
    "Тамара", "Шилова", "Татьяна Геннадьевна", "Муравьева", "Хасанова", "Алина Кузнецова"
]

players = []
roles = {}
order = []
current = 0
last_role_message_id = None
mode = None


# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    for i in range(3, 8):
        kb.button(text=f"{i} игроков", callback_data=f"players_{i}")
    kb.adjust(2)
    await message.answer("Выбери количество игроков:", reply_markup=kb.as_markup())


# выбор количества игроков
@dp.callback_query(lambda c: c.data.startswith("players_"))
async def choose_players(call: types.CallbackQuery):
    global players
    count = int(call.data.split("_")[1])
    players = [f"Игрок {i+1}" for i in range(count)]

    kb = InlineKeyboardBuilder()
    kb.button(text="👤 1 шпион", callback_data="mode_one")

    if count >= 4:
        kb.button(text="🕵️‍♂️ Несколько шпионов", callback_data="mode_many")

    kb.button(text="🎭 Без шпиона", callback_data="mode_none")
    kb.adjust(1)

    await call.message.edit_text("Выбери режим игры:", reply_markup=kb.as_markup())
    await call.answer()


# выбор режима
@dp.callback_query(lambda c: c.data.startswith("mode_"))
async def choose_mode(call: types.CallbackQuery):
    global roles, order, current, mode
    mode = call.data
    current = 0
    order = players.copy()
    roles = {}

    if mode == "mode_one":
        spy = random.choice(players)
        character = random.choice(characters)
        for p in players:
            roles[p] = "Шпион" if p == spy else character

    elif mode == "mode_many":
        spies = random.sample(players, 3)
        character = random.choice(characters)
        for p in players:
            roles[p] = "Шпион" if p in spies else character

    elif mode == "mode_none":
        chars = random.sample(characters, len(players))
        for p, ch in zip(players, chars):
            roles[p] = ch

    kb = InlineKeyboardBuilder()
    kb.button(text="Узнать роль", callback_data="reveal")
    await call.message.edit_text(
        f"Игрок {order[current]}, нажми «Узнать роль»",
        reply_markup=kb.as_markup()
    )
    await call.answer()


# показать роль
@dp.callback_query(lambda c: c.data == "reveal")
async def reveal(call: types.CallbackQuery):
    global last_role_message_id
    player = order[current]
    role = roles[player]

    msg = await call.message.answer(f"{player}, твоя роль:\n\n**{role}**", parse_mode="Markdown")
    last_role_message_id = msg.message_id

    kb = InlineKeyboardBuilder()
    kb.button(text="Скрыть роль", callback_data="hide")
    await call.message.answer("Запомнил? Нажми «Скрыть роль»", reply_markup=kb.as_markup())
    await call.answer()


# скрыть роль
@dp.callback_query(lambda c: c.data == "hide")
async def hide(call: types.CallbackQuery):
    global current

    # 🔥 удаляем сообщение с ролью
    try:
        await bot.delete_message(call.message.chat.id, last_role_message_id)
    except:
        pass

    current += 1
    kb = InlineKeyboardBuilder()

    if current < len(order):
        kb.button(text="Узнать роль", callback_data="reveal")
        await call.message.edit_text(
            f"Игрок {order[current]}, твой ход",
            reply_markup=kb.as_markup()
        )
    else:
        kb.button(text="Показать все роли", callback_data="all")
        await call.message.edit_text("Все посмотрели роли.", reply_markup=kb.as_markup())

    await call.answer()


# показать все роли
@dp.callback_query(lambda c: c.data == "all")
async def show_all(call: types.CallbackQuery):
    text = "\n".join([f"{p}: {r}" for p, r in roles.items()])
    await call.message.edit_text("Роли:\n\n" + text)
    await call.answer()


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
