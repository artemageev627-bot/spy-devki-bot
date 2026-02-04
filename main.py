import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8520367789:AAEWveincfCFZ7KrSPPzfiY0TCNvzR6XIho"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

characters = [
    "Арина Дементьева", "Алина Андриянова", "Руся", "Де линт", "Арина Бетхер",
    "Дуся", "Шутова", "Изобэйнал", "Елена Максимовна", "Марина Юрьевна",
    "Наташа Москвина", "Анжелика", "Михеева", "Игошина", "Марина Попова", "Даша Васильева",
    "Тамара", "Шилова", "Татьяна Геннадьевна", "Муравьева", "Хасанова", "Алина Кузнецова",
    "Шмыкова", "Лера Корепанова", "Лебедева", "Глазырина", "Симонова", "Тарасова",
    "Тараненко", "Исаков", "Смирнов", "Красильников", "Дежин", "Агеев", "Тимофеев",
    "Павлов", "Шуклин", "Бочкарев", "Лобастов", "Созонов", "Злата Понамарева",
    "Альбина", "Саша Васильева", "Катя Кожевникова", "Эвелина", "Аэлита",
    "Кира Жигулина", "Пахан", "Касимов", "Демид", "Тихонов", "Степа",
    "Валентина Григорьевна", "Фазлеева"
]

players = []
roles = {}
order = []
current = 0
mode = None

last_role_message_id = None
last_turn_message_id = None


def players_keyboard():
    kb = InlineKeyboardBuilder()
    for i in range(3, 8):
        kb.button(text=f"{i} игроков", callback_data=f"players_{i}")
    kb.adjust(2)
    return kb.as_markup()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Выбери количество игроков:", reply_markup=players_keyboard())


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


@dp.callback_query(lambda c: c.data.startswith("mode_"))
async def choose_mode(call: types.CallbackQuery):
    global roles, order, current, mode, last_turn_message_id
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

    msg = await call.message.edit_text(
        f"Игрок {order[current]}, нажми «Узнать роль»",
        reply_markup=kb.as_markup()
    )
    last_turn_message_id = msg.message_id
    await call.answer()


@dp.callback_query(lambda c: c.data == "reveal")
async def reveal(call: types.CallbackQuery):
    global last_role_message_id

    # 🔥 удаляем сообщение "твой ход"
    try:
        await bot.delete_message(call.message.chat.id, last_turn_message_id)
    except:
        pass

    player = order[current]
    role = roles[player]

    msg = await call.message.answer(
        f"{player}, твоя роль:\n\n<b>{role}</b>",
        parse_mode="HTML"
    )
    last_role_message_id = msg.message_id

    kb = InlineKeyboardBuilder()
    kb.button(text="Скрыть роль", callback_data="hide")
    await call.message.answer("Запомнил? Нажми «Скрыть роль»", reply_markup=kb.as_markup())
    await call.answer()


@dp.callback_query(lambda c: c.data == "hide")
async def hide(call: types.CallbackQuery):
    global current, last_turn_message_id

    # 🔥 удаляем сообщение с ролью
    try:
        await bot.delete_message(call.message.chat.id, last_role_message_id)
    except:
        pass

    current += 1
    kb = InlineKeyboardBuilder()

    if current < len(order):
        kb.button(text="Узнать роль", callback_data="reveal")
        msg = await call.message.edit_text(
            f"Игрок {order[current]}, твой ход",
            reply_markup=kb.as_markup()
        )
        last_turn_message_id = msg.message_id
    else:
        kb.button(text="Показать все роли", callback_data="all")
        await call.message.edit_text("Все игроки посмотрели роли.", reply_markup=kb.as_markup())

    await call.answer()


@dp.callback_query(lambda c: c.data == "all")
async def show_all(call: types.CallbackQuery):
    text = "\n".join([f"{p}: {r}" for p, r in roles.items()])
    await call.message.edit_text("Роли:\n\n" + text)

    # 🔁 новая игра
    await call.message.answer(
        "Хочешь сыграть ещё раз?",
        reply_markup=players_keyboard()
    )
    await call.answer()


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
