import telebot
from collections import defaultdict
from dotenv import load_dotenv

import callback_handler
import message_handler
import db
import utils
import os


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Let's expand your world of words!")


@bot.message_handler(commands=["add"])
def start_add(message):
    user_states[message.from_user.id] = {"step": "waiting_for_list_name"}

    bot.send_message(message.chat.id, "What list do you want to add?", reply_markup=utils.do_cancel_button())


@bot.message_handler(commands=["view"])
def start_view(message):
    utils.show_lists(bot, message, "view")


@bot.message_handler(commands=["delete"])
def start_delete(message):
    utils.show_lists(bot, message, "delete")


@bot.message_handler(commands=["learn"])
def start_learn(message):
    utils.show_lists(bot, message, "learn")

# TODO correct

@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def handle_user_response(message):
    user_text = message.text
    if user_text == 'Cancel':
        utils.canceling(bot, user_states, message)
        return

    step = user_states[message.from_user.id]['step']

    step_handlers = {
        "waiting_for_list_name": message_handler.waiting_for_list_name,
        "waiting_for_words": message_handler.waiting_for_words,
        "checking": message_handler.checking,
        "waiting_for_answer": message_handler.waiting_for_answer
    }

    handler = step_handlers.get(step)
    if handler:
        handler(bot, user_states, message)
    else:
        bot.send_message(message.chat.id, "Unknown commands. Try again!")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    action, button_name = call.data.split('_')

    if button_name == 'Cancel':
        bot.send_message(call.message.chat.id, f'I have canceled your action.')
        return

    action_handlers = {
        "view": callback_handler.do_view,
        "delete": callback_handler.do_delete,
        "learn": callback_handler.do_learn,
        "learning": callback_handler.do_learning
    }

    handler = action_handlers.get(action)
    if handler:
        handler(bot, user_states, call, button_name)
    else:
        bot.send_message(call.message.chat.id, "Unknown action. Try again!")


db.init_db()
user_states = defaultdict(dict)


if __name__ == "__main__":
    bot.polling(none_stop=True)
