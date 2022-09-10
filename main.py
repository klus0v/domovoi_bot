import telebot
from telebot import types
import json
bot = telebot.TeleBot('%TG_TOKEN%')


@bot.message_handler(commands=['start'])
def start(message):
    f = open('start_message.txt', 'r', encoding='utf-8')
    markup = types.InlineKeyboardMarkup(row_width=1)

    ping_button = types.InlineKeyboardButton(text='пингануть ⏰', callback_data='ping')
    markup.add(ping_button)
    check_button = types.InlineKeyboardButton(text='отметить ✅', callback_data='check')
    markup.add(check_button)

    bot.send_message(message.chat.id, f.read(), reply_markup=markup)
    f.close()

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'ping':
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        water_log = types.InlineKeyboardButton(text='Купить воду', callback_data='water')
        paper_log = types.InlineKeyboardButton(text='Купить туалетку', callback_data='paper')
        trash_log = types.InlineKeyboardButton(text='Купить мешок', callback_data='trash')
        clean_log = types.InlineKeyboardButton(text='Сделать уборку', callback_data='clean')

        item_back = types.InlineKeyboardButton(text=' 🔙 ', callback_data='back')
        keyboard.add(water_log, paper_log, trash_log, clean_log, item_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Что нужно?', reply_markup=keyboard)

    if call.data == 'check':
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        water_log = types.InlineKeyboardButton(text='Купил воду', callback_data='done_water')
        paper_log = types.InlineKeyboardButton(text='Купил туалетку', callback_data='done_paper')
        trash_log = types.InlineKeyboardButton(text='Купил мешок', callback_data='done_trash')
        clean_log = types.InlineKeyboardButton(text='Сделал уборку', callback_data='done_clean')

        item_back = types.InlineKeyboardButton(text=' 🔙 ', callback_data='back')
        keyboard.add(water_log, paper_log, trash_log, clean_log, item_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Что сделал?', reply_markup=keyboard)


    elif call.data == 'water' or call.data == 'paper' or call.data == 'trash' or call.data == 'clean':
        order_file = open('order.json', 'r', encoding='utf-8')
        users_file = open('users.json', 'r', encoding='utf-8')
        order = json.loads(order_file.read())
        users = json.loads(users_file.read())
        user_id = order[call.data]
        user_tg_id = users[str(user_id)]
        order_file.close()
        users_file.close()
        bot.send_message(user_tg_id, "Тебе нужно " + readable_action(call.data))

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start(call.message)
        bot.send_message(call.message.chat.id, "Готово, чувак")

    elif call.data == 'done_water' or call.data == 'done_paper' or call.data == 'done_trash' or call.data == 'done_clean':
        order_file = open('order.json', 'r', encoding='utf-8')
        users_file = open('users.json', 'r', encoding='utf-8')
        order = json.loads(order_file.read())
        users = json.loads(users_file.read())
        user_id = order[call.data[5:]]
        user_tg_id = users[str(user_id)]
        order_file.close()
        users_file.close()

        if user_tg_id != call.from_user.id:
            bot.send_message(call.message.chat.id, "Сейчас не твоя очередь")
            return

        d = open('order.json', 'w')
        order[call.data[5:]] = user_id + 1 if user_id != 5 else 1
        json.dump(order, d)
        d.close()

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start(call.message)
        bot.send_message(call.message.chat.id, "Отметил тебя")

    elif call.data == 'back':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start(call.message)


def readable_action(action):
    if action == "water":
        return "купить воду"
    elif action == "paper":
        return "купить туалетку"
    elif action == "trash":
        return "купить мусорный мешок"
    elif action == "clean":
        return "сделать уборку"
    return "ошибка парсинга"


bot.polling(none_stop=True, interval=0)