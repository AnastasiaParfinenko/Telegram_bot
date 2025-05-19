from telebot.types import ReplyKeyboardRemove
import db
import utils


def do_view(bot, user_states, call, button_name):
    user_id = call.from_user.id

    with db.get_connection() as (conn, cur):
        cur.execute("SELECT word, translation FROM words WHERE user_id = ? AND list_name = ?",
                    (user_id, button_name))
        words = cur.fetchall()

        if words:
            word_list = "\n".join([f"{w[0]} - {w[1]}" for w in words])
            bot.send_message(call.message.chat.id, f"{word_list}", reply_markup=ReplyKeyboardRemove())
        else:
            bot.send_message(call.message.chat.id, "There are no words in this list.",
                             reply_markup=ReplyKeyboardRemove())


def do_delete(bot, user_states, call, button_name):
    user_id = call.from_user.id

    with db.get_connection() as (conn, cur):
        cur.execute("DELETE FROM words WHERE user_id = ? AND list_name = ?",
                    (user_id, button_name))

        bot.send_message(call.message.chat.id, f"The list {button_name} deleted.")

        conn.commit()


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
