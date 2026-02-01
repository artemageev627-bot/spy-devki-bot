import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Персонажи
characters = [
    "Арина Дементьева", "Алина Андриянова", "Руся", "Де линт", "Арина Бетхер",
    "Дуся", "Шутова", "Изобэйнал", "Елена Максимовна", "Марина Юрьевна",
    "Наташа Москвина", "Анжелика", "Михеева", "Игошина", "Марина", "Даша",
    "Тамара", "Шилова", "Татьяна Геннадьевна", "Муравьева", "Хасанова", "Алина Кузнецова"
]

# Переменные игры
players = []
roles = {}
player_order = []
current_player_index = 0

# Стартовая команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("3 игрока", callback_data="3"),
         InlineKeyboardButton("4 игрока", callback_data="4")],
        [InlineKeyboardButton("5 игроков", callback_data="5"),
         InlineKeyboardButton("6 игроков", callback_data="6")],
        [InlineKeyboardButton("7 игроков", callback_data="7")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите количество игроков:", reply_markup=reply_markup)

# Выбор количества игроков и назначение ролей
async def choose_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global players, roles, player_order, current_player_index
    query = update.callback_query
    await query.answer()

    num_players = int(query.data)
    players = [f"Игрок {i+1}" for i in range(num_players)]

    spy = random.choice(players)
    character = random.choice(characters)

    roles = {player: ("Шпион" if player == spy else character) for player in players}
    player_order = players.copy()
    current_player_index = 0

    # Кнопка для первого игрока
    keyboard = [[InlineKeyboardButton("Узнать роль", callback_data="reveal")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Роли назначены! Игрок {player_order[current_player_index]}, нажмите 'Узнать роль'.", reply_markup=reply_markup)

# Показ роли игроку
async def reveal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_player_index
    query = update.callback_query
    await query.answer()

    player = player_order[current_player_index]
    role = roles[player]

    # Показ роли текущему игроку
    await query.edit_message_text(f"{player}, твоя роль: {role}")

    # Кнопка скрыть роль
    keyboard = [[InlineKeyboardButton("Скрыть роль", callback_data="hide")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Когда запомнил роль, нажми 'Скрыть роль'", reply_markup=reply_markup)

# Переход к следующему игроку или финалу
async def hide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_player_index
    query = update.callback_query
    await query.answer()

    current_player_index += 1
    if current_player_index < len(player_order):
        keyboard = [[InlineKeyboardButton("Узнать роль", callback_data="reveal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"Игрок {player_order[current_player_index]}, нажмите 'Узнать роль'", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("Показать все роли", callback_data="show_all")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Все игроки посмотрели свои роли.", reply_markup=reply_markup)

# Показ всех ролей
async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    all_roles = "\n".join([f"{p}: {r}" for p, r in roles.items()])
    await query.edit_message_text(f"Все роли:\n{all_roles}")

if __name__ == "__main__":
    # Вставь свой токен вместо "YOUR_BOT_TOKEN_HERE"
    app = ApplicationBuilder().token("8520367789:AAEWveincfCFZ7KrSPPzfiY0TCNvzR6XIho").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_players, pattern="^[3-7]$"))
    app.add_handler(CallbackQueryHandler(reveal, pattern="^reveal$"))
    app.add_handler(CallbackQueryHandler(hide, pattern="^hide$"))
    app.add_handler(CallbackQueryHandler(show_all, pattern="^show_all$"))

    print("Бот запущен...")
    app.run_polling()
