import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

# Вставь сюда токен бота
BOT_TOKEN = "8520367789:AAEWveincfCFZ7KrSPPzfiY0TCNvzR6XIho"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Персонажи
characters = [
    "Арина Дементьева", "Алина Андриянова", "Руся", "Де линт", "Арина Бетхер",
    "Дуся", "Шутова", "Изобэйнал", "Елена Максимовна", "Марина Юрьевна",
    "Наташа Москвина", "Анжелика", "Михеева", "Игошина", "Марина", "Даша",
    "Тамара", "Шилова", "Татьяна Геннадьевна", "Муравьева", "Хасанова", "Алина Кузнецова"
]

# Игровые переменные
players = []
roles = {}
player_order = []
current_player_index = 0

# --- Команда /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="3 игрока", callback_data="3"),
        InlineKeyboardButton(text="4 игрока", callback_data="4")
    )
    builder.row(
        InlineKeyboardButton(text="5 игроков", callback_data="5"),
        InlineKeyboardButton(text="6 игроков", callback_data="6")
    )
    builder.row(
        InlineKeyboardButton(text="7 игроков", callback_data="7")
    )
    await message.answer("Выберите количество игроков:", reply_markup=builder.as_markup())

# --- Выбор игроков ---
@dp.callback_query(lambda c: c.data in ["3","4","5","6","7"])
async def choose_players(callback: types.CallbackQuery):
    global players, roles, player_order, current_player_index
    await callback.answer()
    num_players = int(callback.data)
    players = [f"Игрок {i+1}" for i in range(num_players)]

    spy = random.choice(players)
    character = random.choice(characters)
    roles = {player: ("Шпион" if player == spy else character) for player in players}
    player_order = players.copy()
    current_player_index = 0

    # Кнопка для первого игрока
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Узнать роль", callback_data="reveal"))
    await callback.message.edit_text(f"Роли назначены! Игрок {player_order[current_player_index]}, нажмите 'Узнать роль'.",
                                     reply_markup=builder.as_markup())

# --- Показ роли игроку ---
@dp.callback_query(lambda c: c.data=="reveal")
async def reveal(callback: types.CallbackQuery):
    global current_player_index
    await callback.answer()
    player = player_order[current_player_index]
    role = roles[player]

    await callback.message.edit_text(f"{player}, твоя роль: {role}")

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Скрыть роль", callback_data="hide"))
    await callback.message.answer("Когда запомнил роль, нажми 'Скрыть роль'", reply_markup=builder.as_markup())

# --- Скрытие роли и переход к следующему игроку ---
@dp.callback_query(lambda c: c.data=="hide")
async def hide(callback: types.CallbackQuery):
    global current_player_index
    await callback.answer()
    current_player_index += 1

    builder = InlineKeyboardBuilder()
    if current_player_index < len(player_order):
        builder.add(InlineKeyboardButton(text="Узнать роль", callback_data="reveal"))
        await callback.message.edit_text(f"Игрок {player_order[current_player_index]}, нажмите 'Узнать роль'",
                                         reply_markup=builder.as_markup())
    else:
        builder.add(InlineKeyboardButton(text="Показать все роли", callback_data="show_all"))
        await callback.message.edit_text("Все игроки посмотрели свои роли.", reply_markup=builder.as_markup())

# --- Показ всех ролей ---
@dp.callback_query(lambda c: c.data=="show_all")
async def show_all(callback: types.CallbackQuery):
    await callback.answer()
    all_roles = "\n".join([f"{p}: {r}" for p, r in roles.items()])
    await callback.message.edit_text(f"Все роли:\n{all_roles}")

# --- Запуск бота ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
