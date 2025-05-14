import telebot
from collections import defaultdict
import db
import utils
from dotenv import load_dotenv
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
def start_delete(message):
    utils.show_lists(bot, message, "learn")


db.init_db()
user_states = defaultdict(dict)

import message_handler
import callback_handler

if __name__ == "__main__":
    bot.polling(none_stop=True)
