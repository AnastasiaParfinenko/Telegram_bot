from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import ReplyKeyboardRemove
import db


def canceling(bot, user_states, message):
    bot.send_message(message.chat.id, f"Ok, I canceled your action!", reply_markup=ReplyKeyboardRemove())
    del user_states[message.from_user.id]


def show_lists(bot, message, action):
    user_id = message.from_user.id
    lists = db.get_user_lists(user_id)

    if not lists:
        bot.send_message(message.chat.id, f"There are no lists to {action}.")
        return False

    markup = InlineKeyboardMarkup()
    for list_name in lists:
        markup.add(InlineKeyboardButton(list_name, callback_data=f'{action}_{list_name}'))
    markup.add(InlineKeyboardButton('Cancel', callback_data=f'{action}_Cancel'))

    bot.send_message(message.chat.id, f"Choose a list to {action}.", reply_markup=markup)


def show_word_list(bot, call, words):
    if words:
        word_list = "\n".join([f"{w[0]}: {w[1]}" for w in words])
        bot.send_message(call.message.chat.id, f"{word_list}", reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(call.message.chat.id, "There are no words in this list.",
                         reply_markup=ReplyKeyboardRemove())


def show_action_to_learn(bot, message):
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton('Write the word', callback_data='learning_writing')
    button2 = InlineKeyboardButton('Flashcards', callback_data='learning_flashcards')
    markup.add(button1, button2)

    bot.send_message(message.chat.id, 'Choose your mode: Flashcards or Write the word?', reply_markup=markup)


def show_translation_direction(bot, call):
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton('RU -> DE', callback_data='learning_rude')
    button2 = InlineKeyboardButton('DE -> RU', callback_data='learning_deru')
    markup.add(button1, button2)

    bot.send_message(call.message.chat.id,'Choose the translation direction: From Russian to German or From German to Russian?', reply_markup=markup)


def do_cancel_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Cancel'))
    return markup


def work_with_flashcards(bot, user_states, first_side, message_or_call):
    if hasattr(message_or_call, 'chat'):
        chat_id = message_or_call.chat.id
        user_id = message_or_call.from_user.id
    else:
        chat_id = message_or_call.message.chat.id
        user_id = message_or_call.from_user.id

    if user_states[user_id]['flashcards']:
        side = first_side == 'ru'
        card = user_states[user_id]['flashcards'][-1]

        user_states[user_id]['step'] = 'checking'
        bot.send_message(
            chat_id,
            f"\u200B\n*{card[side]}*\n\u200B",
            parse_mode="Markdown",
            reply_markup=flashcard_check_buttons()
        )
    else:
        del user_states[user_id]
        bot.send_message(chat_id, 'The list ended! Good job!')


def flashcard_check_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton('Check')
    cancel_button = KeyboardButton('Cancel')
    markup.add(cancel_button, button)
    return markup


def flashcard_evaluation_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("Cancel"), KeyboardButton("Right"))
    markup.row(KeyboardButton("Wrong"))
    return markup