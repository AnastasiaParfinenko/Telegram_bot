from bot import bot, user_states
import utils
from telebot.types import ReplyKeyboardRemove
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import re
import db

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_user_response(message):
    user_id = message.from_user.id
    state = user_states[user_id]

    user_text = message.text
    if user_text == 'Cancel':
        bot.send_message(message.chat.id, f"Ok, I canceled your action!", reply_markup=ReplyKeyboardRemove())
        del user_states[user_id]

    elif state["step"] == "waiting_for_list_name":
        user_states[user_id]["list_name"] = user_text
        user_states[user_id]["step"] = "waiting_for_words"
        bot.send_message(message.chat.id, "Sent me a list of words in the format: word – translate", reply_markup=utils.do_cancel_button())

    elif state["step"] == "waiting_for_words":
        list_name = state["list_name"]
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

    elif state['step'] == 'checking':
        side = state['first_side'] != 'ru'
        card = state['flashcards'][-1]

        user_states[user_id]['step'] = 'waiting_for_answer'

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_button = KeyboardButton(text='Cancel')
        right_button = KeyboardButton(text='Right')
        wrong_button = KeyboardButton(text='Wrong')

        markup.row(cancel_button, right_button)
        markup.row(wrong_button)

        bot.send_message(message.chat.id,
                         f"\u200B\n*{card[side]}*\n\u200B",
                         parse_mode="Markdown",
                         reply_markup=markup)

    elif state['step'] == 'waiting_for_answer':
        user_states[user_id]['step'] = 'flashcards'
        flashcards = state['flashcards']
        if user_text == 'Wrong':
            flashcards.insert(0, flashcards[-1])
        flashcards.pop()
        utils.work_with_flashcards(bot, user_states, user_states[user_id]['first_side'], message)
