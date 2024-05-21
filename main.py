import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('YOUR_TOKEN')
ADMIN_CHAT_IDS = ['6693635890', '6401268984']

# Подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Создание таблицы для хранения заявок пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
                  user_id INTEGER PRIMARY KEY,
                  team TEXT,
                  profits INTEGER,
                  status TEXT DEFAULT 'pending'
                  )''')
conn.commit()

@bot.message_handler(commands=['start', 'menu'])
def send_menu(message):
    user_id = message.from_user.id
    # Проверяем статус заявки пользователя
    cursor.execute("SELECT status FROM applications WHERE user_id=?", (user_id,))
    application_status = cursor.fetchone()
    if application_status is None or application_status[0] == 'rejected':
        bot.send_message(message.chat.id, "Для доступа к меню бота подайте заявку. Ответьте на следующие вопросы:\n"
                                          "1. В каких тимах работали?\n"
                                          "2. Сумма ваших профитов?")
    else:
        # Показываем меню бота, если заявка прошла
        markup = types.InlineKeyboardMarkup(row_width=3)
        button1 = types.InlineKeyboardButton("🔍Запросить парс", callback_data="button1_pressed")
        button2 = types.InlineKeyboardButton("⏳Очередь", callback_data="button2_pressed")
        button3 = types.InlineKeyboardButton("👑Администрация бота", callback_data="button3_pressed")
        markup.row(button1, button2, button3)
        bot.send_message(message.chat.id, "Добро пожаловать в Lavoro Parser!\n"
                                          "🤖Меню бота:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith('/apply'))
def apply_for_access(message):
    # Обработка заявки на доступ
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Для доступа к боту, пожалуйста, ответьте на следующие вопросы:\n"
                                      "1. В каких тимах работали?\n"
                                      "2. Сумма ваших профитов?")
    # Изменение статуса пользователя на 'applying'
    cursor.execute("INSERT OR IGNORE INTO applications (user_id, status) VALUES (?, 'applying')", (user_id,))
    conn.commit()

@bot.message_handler(func=lambda message: message.text.startswith('/answer'))
def answer_to_application(message):
    # Обработка ответа на вопросы для заявки
    user_id = message.from_user.id
    answers = message.text.split('\n')
    if len(answers) == 3:
        team = answers[1]
        profits = answers[2]
        cursor.execute("UPDATE applications SET team=?, profits=?, status='pending' WHERE user_id=?", (team, profits, user_id))
        conn.commit()
        bot.send_message(message.chat.id, "Ваша заявка на доступ обработана.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте на оба вопроса.")



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
@bot.message_handler(commands=['view_applications'])
def view_applications(message):
    # Просмотр заявок пользователей (только для админов)
    if str(message.chat.id) in ADMIN_CHAT_IDS:
        cursor.execute("SELECT * FROM applications")
        applications = cursor.fetchall()
        if applications:
            response = "Список заявок пользователей:\n"
            for application in applications:
                response += f"User ID: {application[0]}, Team: {application[1]}, Profits: {application[2]}, Status: {application[3]}\n"
        else:
            response = "На данный момент заявок нет."
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

@bot.message_handler(commands=['accept'])
def accept_application(message):
    # Одобрение заявки пользователя (только для админов)
    if str(message.chat.id) in ADMIN_CHAT_IDS:
        user_id = message.text.split()[1]
        cursor.execute("UPDATE applications SET status='accepted' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, f"Заявка пользователя с ID {user_id} одобрена.")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

@bot.message_handler(commands=['reject'])
def reject_application(message):
    # Отклонение заявки пользователя (только для админов)
    if str(message.chat.id) in ADMIN_CHAT_IDS:
        user_id = message.text.split()[1]
        cursor.execute("UPDATE applications SET status='rejected' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, f"Заявка пользователя с ID {user_id} отклонена.")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

bot.polling()
