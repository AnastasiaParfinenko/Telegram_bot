import utils
from telebot.types import ReplyKeyboardRemove
import db


def waiting_for_list_name(bot, user_states, message):
    user_id = message.from_user.id
    user_text = message.text

    user_states[user_id]["list_name"] = user_text
    user_states[user_id]["step"] = "waiting_for_words"
    text = "Sent me a list of words in the format: word: translate"
    bot.send_message(message.chat.id, text, reply_markup=utils.do_cancel_button())
    # TODO: consider the case of the existence of a list


def waiting_for_words(bot, user_states, message):
    user_id = message.from_user.id
    user_text = message.text
    list_name = user_states[user_id]["list_name"]
    words = user_text.split("\n")

    db.delete_list(user_id, list_name)
    error_lines = db.create_list(user_id, list_name, words)
    if error_lines:
        error_text = "There are errors in the following lines:\n" + "\n".join(error_lines)
        bot.send_message(message.chat.id, error_text, reply_markup=ReplyKeyboardRemove())
    #TODO: what to do with the error_lines?

    text = f"The list '{list_name}' {user_states[user_id]['action']}ed!"
    bot.send_message(message.chat.id, text, reply_markup=ReplyKeyboardRemove())
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
