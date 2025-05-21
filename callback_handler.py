from telebot.types import ReplyKeyboardRemove
import db
import utils


def do_view(bot, user_states, call, button_name):
    words = db.get_word_list(call.from_user.id, button_name)
    utils.show_word_list(bot, call, words)


def do_delete(bot, user_states, call, button_name):
    db.delete_list(call.from_user.id, button_name)
    bot.send_message(call.message.chat.id, f"The list {button_name} deleted.")


def do_correct(bot, user_states, call, button_name):
    do_view(bot, user_states, call, button_name)

    user_id = call.from_user.id
    user_states[user_id]["list_name"] = button_name
    user_states[user_id]["step"] = "waiting_for_words"

    text = f"Sent me a new list of words in the format: word: translate"
    bot.send_message(call.message.chat.id, text , reply_markup=utils.do_cancel_button())


def do_learn(bot, user_states, call, button_name):
    user_id = call.from_user.id
    user_states[user_id] = {'step': 'learning'}
    user_states[user_id]['flashcards'] = db.get_flashcards(user_id, button_name)
    utils.show_action_to_learn(bot, call.message)


def do_learning(bot, user_states, call, button_name):
    user_id = call.from_user.id

    if button_name == 'flashcards':
        user_states[user_id]['step'] = 'flashcards'
        utils.show_translation_direction(bot, call)
    elif button_name == 'writing':
        bot.send_message(call.message.chat.id, f"Сщас сложно будет!")
    # TODO
    elif button_name == 'quiz':
        bot.send_message(call.message.chat.id, f"Выбери верный вариант.")
    elif button_name == 'rude':
        user_states[user_id]['first_side'] = 'ru'
        utils.work_with_flashcards(bot, user_states,"ru", call)
    elif button_name =='deru':
        user_states[user_id]['first_side'] = 'de'
        utils.work_with_flashcards(bot, user_states,"de", call)
    else:
        bot.send_message(call.message.chat.id, f"{button_name} и что-то пошло не так!")
