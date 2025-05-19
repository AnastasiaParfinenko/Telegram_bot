import utils
from telebot.types import ReplyKeyboardRemove
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import re
import db


def waiting_for_list_name(bot, user_states, message):
    user_id = message.from_user.id
    user_text = message.text

    user_states[user_id]["list_name"] = user_text
    user_states[user_id]["step"] = "waiting_for_words"
    bot.send_message(message.chat.id, "Sent me a list of words in the format: word – translate", reply_markup=utils.do_cancel_button())


def waiting_for_words(bot, user_states, message):
    user_id = message.from_user.id
    user_text = message.text
    list_name = user_states[user_id]["list_name"]
    words = user_text.split("\n")

    with db.get_connection() as (conn, cur):

        for line in words:
            try:
                word, translation = re.split(r'[-—]{1,2}\s*', line, maxsplit=1)
                cur.execute("INSERT INTO words (user_id, list_name, word, translation) VALUES (?, ?, ?, ?)",
                            (user_id, list_name, word.strip(), translation.strip()))
            except ValueError:
                bot.send_message(message.chat.id, f"There is a mistake: {line}.", reply_markup=ReplyKeyboardRemove())

        bot.send_message(message.chat.id, f"The list '{list_name}' added!", reply_markup=ReplyKeyboardRemove())

        conn.commit()
    del user_states[user_id]


def checking(bot, user_states, message):
    user_id = message.from_user.id
    side = user_states[user_id]['first_side'] != 'ru'
    card = user_states[user_id]['flashcards'][-1]

    user_states[user_id]['step'] = 'waiting_for_answer'

    bot.send_message(message.chat.id,
                     f"\u200B\n*{card[side]}*\n\u200B",
                     parse_mode="Markdown",
                     reply_markup=utils.flashcard_evaluation_buttons())


def waiting_for_answer(bot, user_states, message):
    user_id = message.from_user.id
    user_text = message.text
    user_states[user_id]['step'] = 'checking'
    flashcards = user_states[user_id]['flashcards']
    if user_text == 'Wrong':
        flashcards.insert(0, flashcards[-1])
    flashcards.pop()
    utils.work_with_flashcards(bot, user_states, user_states[user_id]['first_side'], message)
