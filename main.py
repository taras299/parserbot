import telebot
from telebot import types
import re
import sqlite3

bot = telebot.TeleBot('6492078155:AAGD8wYe38GLMfslAcNxNFegvst3UA1FcbA')
ADMIN_CHAT_IDS = ['6693635890', '6401268984']

conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    team TEXT,
    profit INTEGER,
    application_status TEXT
)
''')

conn.commit()

@bot.message_handler(commands=['start', 'menu'])
def send_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton("🔍Запросить парс", callback_data="button1_pressed")
    button2 = types.InlineKeyboardButton("⏳Очередь", callback_data="button2_pressed")
    button3 = types.InlineKeyboardButton("👑Администрация бота", callback_data="button3_pressed")
    markup.row(button1, button2, button3)
    bot.send_message(message.chat.id, "Добро пожаловать в Lavoro Parser!\n"
                                      "🤖Меню бота:", reply_markup=markup)

# Ответы на вопросы для подачи заявки
questions = {}
@bot.message_handler(commands=['apply'])
def start_application(message):
    questions[message.from_user.id] = {'team': None, 'profit': None}
    bot.send_message(message.chat.id, "Для подачи заявки ответьте на следующие вопросы:\n1. В каких тимах работали?\n2. Сумма ваших профитов?")

@bot.message_handler(func=lambda message: message.from_user.id in questions and questions[message.from_user.id]['team'] is None)
def handle_team(message):
    questions[message.from_user.id]['team'] = message.text
    bot.send_message(message.chat.id, "Отлично! Теперь введите сумму ваших профитов:")

@bot.message_handler(func=lambda message: message.from_user.id in questions and questions[message.from_user.id]['team'] is not None)
def handle_profit(message):
    try:
        profit = int(message.text)
        questions[message.from_user.id]['profit'] = profit
        save_application(message.from_user.id, questions[message.from_user.id]['team'], profit)
        bot.send_message(message.chat.id, "Спасибо! Ваша заявка принята.")
        del questions[message.from_user.id]
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное число для суммы профитов.")

def save_application(user_id, team, profit):
    cursor.execute('INSERT INTO users (user_id, username, team, profit, application_status) VALUES (?, ?, ?, ?, ?)',
                   (user_id, 'test', team, profit, 'pending'))
    conn.commit()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "button1_pressed":
        bot.answer_callback_query(call.id, "⏳Запрашиваю парс...")
        send_parsing_options(call.message)
    elif call.data == "button2_pressed":
        bot.answer_callback_query(call.id, "⏳Загружаю очередь...")
        bot.send_message(call.message.chat.id, "👥Очередь в парсере: 1")
    elif call.data == "button3_pressed":
        bot.answer_callback_query(call.id, "⏳Загружаю админов...")
        bot.send_message(call.message.chat.id,
                         "🤴Админ состав:\n"
                         "@Nutcraker❤️\n"
                         "@Dobruy_Na_Svyazi❤️")

def send_parsing_options(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    button4 = types.InlineKeyboardButton("Soul Parser", callback_data="button4_pressed")
    button5 = types.InlineKeyboardButton("Void Parser  ", callback_data="button5_pressed")
    button6 = types.InlineKeyboardButton("Любой", callback_data="button6_pressed")
    markup.row(button4, button5, button6)
    bot.send_message(message.chat.id, "🔍Выберите необходимый парсер:", reply_markup=markup)

@bot.message_handler(func=lambda message: len(re.findall(r'http[s]?://[^\s]+', message.text)) >= 3 and len(
    re.findall(r'http[s]?://[^\s]+', message.text)) <= 6)
def handle_links(message):
    links = re.findall(r'http[s]?://[^\s]+', message.text)
    if len(links) >= 3 and len(links) <= 6:
        username = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} {message.from_user.last_name}"
        user_info = f"🗣Воркер {username} | ({message.from_user.id}) Прислал ссылки для парсинга:\n\n" + "\n".join(links)

        for admin_id in ADMIN_CHAT_IDS:
            bot.send_message(admin_id, user_info)

        bot.send_message(message.chat.id, "✅Готово! Ваши ссылки получены и поставлены в очередь на обработку. Ожидайте выдачи🕒")

bot.polling()
