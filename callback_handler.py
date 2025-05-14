from bot import bot, user_states
from telebot.types import ReplyKeyboardRemove
import db
import utils


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    action, button_name = call.data.split('_')
    user_id = call.from_user.id

    with db.get_connection() as (conn, cur):

        if button_name == 'Cancel':
            bot.send_message(call.message.chat.id, f'I have canceled your action.')

        elif action == 'view':
            cur.execute("SELECT word, translation FROM words WHERE user_id = ? AND list_name = ?",
                        (user_id, button_name))
            words = cur.fetchall()

            if words:
                word_list = "\n".join([f"{w[0]} - {w[1]}" for w in words])
                bot.send_message(call.message.chat.id, f"{word_list}", reply_markup=ReplyKeyboardRemove())
            else:
                bot.send_message(call.message.chat.id, "There are no words in this list.",
                                 reply_markup=ReplyKeyboardRemove())

        elif action == 'delete':
            cur.execute("DELETE FROM words WHERE user_id = ? AND list_name = ?",
                        (user_id, button_name))

            bot.send_message(call.message.chat.id, f"The list {button_name} deleted.")

            conn.commit()

        elif action == 'learn':
            user_states[user_id] = {'step': 'learning'}
            user_states[user_id]['flashcards'] = db.get_flashcards(user_id, button_name)
            utils.show_action_to_learn(bot, call.message)

        elif action == 'learning':
            if button_name == 'flashcards':
                user_states[user_id]['step'] = 'flashcards'
                utils.show_translation_direction(bot, call)
            elif button_name == 'writing':
                bot.send_message(call.message.chat.id, f"Сщас сложно будет!")
            elif button_name == 'quiz':
                bot.send_message(call.message.chat.id, f"Выбери верный вариант.")
            elif button_name == 'rude':
                user_states[user_id]['first_side'] = 'ru'
                utils.work_with_flashcards(bot, user_states,"ru", call)
            elif button_name =='deru':
                user_states[user_id]['first_side'] = 'de'
                print(call.from_user.id)
                utils.work_with_flashcards(bot, user_states,"de", call)
            else:
                bot.send_message(call.message.chat.id, f"{button_name} и что-то пошло не так!")

        else:
            bot.send_message(call.message.chat.id, f"{action} и что-то пошло не так!")