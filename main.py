import telebot
from telebot import types
import re

bot = telebot.TeleBot('6492078155:AAGD8wYe38GLMfslAcNxNFegvst3UA1FcbA')
ADMIN_CHAT_IDS = ['6693635890', '6401268984']

@bot.message_handler(commands=['start', 'menu'])
def send_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton("🔍Запросить парс", callback_data="button1_pressed")
    button2 = types.InlineKeyboardButton("⏳Очередь", callback_data="button2_pressed")
    button3 = types.InlineKeyboardButton("👑Администрация бота", callback_data="button3_pressed")
    markup.row(button1, button2, button3)
    bot.send_message(message.chat.id, "Добро пожаловать в Lavoro Parser!\n"
                                      "🤖Меню бота:", reply_markup=markup)

@bot.message_handler(commands=['parsing'])
def send_parsing_options(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    button4 = types.InlineKeyboardButton("Soul Parser", callback_data="button4_pressed")
    button5 = types.InlineKeyboardButton("Void Parser  ", callback_data="button5_pressed")
    button6 = types.InlineKeyboardButton("Любой", callback_data="button6_pressed")
    markup.row(button4, button5, button6)
    bot.send_message(message.chat.id, "🔍Выберите необходимый парсер:", reply_markup=markup)

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
    elif call.data == "button4_pressed":
        bot.answer_callback_query(call.id, "Soul")
        bot.send_message(call.message.chat.id,
                         "✅Отлично! Вы выбрали Soul! Пришлите от 3-х до 6-ти ссылок на категории в одном сообщении!")
    elif call.data == "button5_pressed":
        bot.answer_callback_query(call.id, "Void")
        bot.send_message(call.message.chat.id,
                         "✅Отлично! Вы выбрали Void! Пришлите от 3-х до 6-ти ссылок на категории в одном сообщении!")
    elif call.data == "button6_pressed":
        bot.answer_callback_query(call.id, "Любой")
        bot.send_message(call.message.chat.id,
                         "✅Отлично! Пришлите от 3-х до 6-ти ссылок на категории в одном сообщении!")

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
