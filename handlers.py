import os
import re

from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ForceReply, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from settings import WELCOME_MESSAGE, TELEGRAM_SUPPORT_CHAT_ID, TELEGRAM_SUPERCHAT_ID
from db import *

user_questions = dict()
main_channel = int(-1001525702468)
main_chat = int(-1001610448157)

curators = {
    -1001764887260: -1001530512275,
    -1001178196959: -1001526061429,
    -1001198171192: -1001198171192,
}

curators_queue = list(curators.keys())
def __init__(self):
    global main_channel
    global main_chat
    global user_questions
    global curators
    global curators_queue
    user_questions[0] = 1


def start(update, context):
    #     update.message.reply_text(WELCOME_MESSAGE, reply_markup=ForceReply(force_reply=True, input_field_placeholder = "Задайте свой вопрос"))
    print('/start')
    custom_keyboard = [['Задать вопрос']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)

    user_telegram_id = update.message.from_user.id
    if not check_by_telegram_id(user_telegram_id):
        custom_keyboard = []
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text(
            'Добро пожаловать в ряды студентов Академии Нутрициологии💚\n\nРады приветствовать в боте-куратора, где ты можешь задавать вопросы и получать ответы от врачей превентивной медицины.\n⠀\n⁉️Запустив в бот, ты соглашаешься с его правилами:⁉️\n⠀\n📍стараться формулировать вопросы в рамках обучающей программы: нутрициология, физиология, диетология и т.д.\n⠀\n📍запрещены консультации по заболеваниям, которые не проходили на курсе, так они требуют врачебного подхода и индивидуального рассмотрения\n⠀\n📍запрещены консультации по препаратам и БАДам, которые не проходили на курсе, но постараемся найти для вас актуальную научную информацию.',
            reply_markup=reply_markup)
        update.message.reply_text(
            'Перед началом работы надо авторизоваться. Введите свой номер телефона, записанный на платформе',
            reply_markup=reply_markup)
        return

    update.message.reply_text(
        'Добро пожаловать в ряды студентов Академии Нутрициологии💚\n\nРады приветствовать в боте-куратора, где ты можешь задавать вопросы и получать ответы от врачей превентивной медицины.\n⠀\n⁉️Запустив в бот, ты соглашаешься с его правилами:⁉️\n⠀\n📍стараться формулировать вопросы в рамках обучающей программы: нутрициология, физиология, диетология и т.д.\n⠀\n📍запрещены консультации по заболеваниям, которые не проходили на курсе, так они требуют врачебного подхода и индивидуального рассмотрения\n⠀\n📍запрещены консультации по препаратам и БАДам, которые не проходили на курсе, но постараемся найти для вас актуальную научную информацию.\n\nНажимай кнопку "Задать вопрос" и получи первый ответ)',
        reply_markup=reply_markup)


def setup_dispatcher(dp):
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('^Задать вопрос$'), new_question))
    dp.add_handler(MessageHandler(Filters.regex('^Вопрос решен$'), close_problem))

    dp.add_handler(MessageHandler(Filters.chat_type.private, handle_user_message))

    dp.add_handler(MessageHandler(Filters.chat(main_chat) & Filters.reply, handle_curator_message))

    dp.add_handler(
        MessageHandler(Filters.chat(main_chat) & Filters.forwarded_from(chat_id=main_channel),
                       update_pinned))

    for curator_channel, curator_chat in curators.items():
        dp.add_handler(MessageHandler(Filters.chat(curator_chat) & Filters.reply, handle_curator_message))
        dp.add_handler(
            MessageHandler(Filters.chat(int(curator_chat)) & Filters.forwarded_from(chat_id=int(curator_channel)),
                           update_pinned))

    dp.add_handler(MessageHandler(Filters.all, handle_message))
    dp.add_handler(CallbackQueryHandler(first_submenu,
                                        pattern='^.*es.*$'))
    return dp


def new_question(update, context):
    user_telegram_id = update.message.from_user.id

    if not check_by_telegram_id(user_telegram_id):
        update.message.reply_text(
            'Вы не авторизованы')
        return

    custom_keyboard = [['Вопрос решен']]
    user_chat_id = update.message.chat.id

    if not user_chat_id in user_questions:
        reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text("Опишите свой вопрос и нажмите отправить", reply_markup=reply_markup)
        user_questions[user_chat_id] = {
            'status': 0,
            'username': find_user_by_telegram(user_telegram_id)['phone']
        }
        # user_questions[user_chat_id]['status'] = 2

    elif user_questions[user_chat_id]['status'] == 4:
        pass;
    else:
        reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text("У вас уже задан вопрос", reply_markup=reply_markup)


def handle_user_message(update, context):
    user_chat_id = update.message.chat.id

    custom_keyboard = [['Задать вопрос']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)

    user_telegram_id = update.message.from_user.id

    if not check_by_telegram_id(user_telegram_id):
        user_in_system = check_and_insert(update.message.text, user_telegram_id)
        if user_in_system is None:
            update.message.reply_text(
                'Не найдено активного курса с таким номером')
            return
        elif not user_in_system:
            update.message.reply_text(
                'Номер уже активирован')
            return
        elif user_in_system:
            update.message.reply_text(
                'Чтобы задать вопрос нажмите кнопку "Задать вопрос"',
                reply_markup=reply_markup)
        return

    if not user_chat_id in user_questions:
        custom_keyboard = [['Задать вопрос']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text('Чтобы задать вопрос нажмите кнопку "Задать вопрос"', reply_markup=reply_markup)
    elif user_questions[user_chat_id]['status'] == 0:
        if not update.message.text:
            custom_keyboard = [['Вопрос решен']]
            reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
            update.message.reply_text("Вопрос должен быть текстовым!", reply_markup=reply_markup)
        else:

            new_message = context.bot.send_message(
                chat_id=main_channel,
                text=(user_questions[user_chat_id]['username'] + '\n' + update.message.text)
            )

            user_questions[user_chat_id]['status'] = 1
            user_questions[user_chat_id]['curator_id'] = get_curator()
            user_questions[user_chat_id]['main_channel_message_id'] = new_message.message_id

            new_message_to_curator = context.bot.send_message(
                chat_id=user_questions[user_chat_id]['curator_id'],
                text=(user_questions[user_chat_id]['username'] + '\n' + update.message.text)
            )
            user_questions[user_chat_id]['curator_channel_message_id'] = new_message_to_curator.message_id
    elif user_questions[user_chat_id]['status'] == 1:
        update.message.reply_text("Ожидайте, подбирается куратор.")
    elif user_questions[user_chat_id]['status'] == 2:

        to_main_chat = context.bot.copy_message(
            chat_id=main_chat,
            reply_to_message_id=user_questions[user_chat_id]['main_chat_message_id'],
            message_id=update.message.message_id,
            from_chat_id=update.message.chat_id
        )
        to_curator_chat = context.bot.copy_message(
            chat_id=curators[user_questions[user_chat_id]['curator_id']],
            reply_to_message_id=user_questions[user_chat_id]['curator_chat_message_id'],
            message_id=update.message.message_id,
            from_chat_id=update.message.chat_id
        )
    elif user_questions[user_chat_id]['status'] == 4:
        custom_keyboard = [['Задать вопрос']]
        reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text("Спасибо за ответ!", reply_markup=reply_markup)
        last = user_questions.pop(user_chat_id, None)

        to_main_chat = context.bot.copy_message(
            chat_id=main_chat,
            reply_to_message_id=last['main_chat_message_id'],
            message_id=update.message.message_id,
            from_chat_id=update.message.chat_id
        )


def close_problem(update, context):
    user_chat_id = update.message.chat.id
    if not user_chat_id in user_questions or user_questions[user_chat_id]['status'] == 0:
        custom_keyboard = [['Задать вопрос']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text('Вы не задали свой вопрос', reply_markup=reply_markup)

    elif user_questions[user_chat_id]['status'] == 2:

        reply_markup = on_end_estimate_keyboard()
        update.message.reply_text("Вопрос закрыт, поставьте оценку", reply_markup=reply_markup)

        context.bot.send_message(
            chat_id=main_chat,
            text='Вопрос закрыт пользователем',
            reply_to_message_id=user_questions[user_chat_id]['main_chat_message_id']
        )

        context.bot.send_message(
            chat_id=curators[user_questions[user_chat_id]['curator_id']],
            text='Вопрос закрыт пользователем',
            reply_to_message_id=user_questions[user_chat_id]['curator_chat_message_id']
        )
        user_questions[user_chat_id]['status'] = 3
    elif user_questions[user_chat_id]['status'] == 3:
        update.message.reply_text("Пожалуйста, поставьте оценку", reply_markup=on_end_estimate_keyboard())


def handle_message(update, context):
    pass;


def on_end_estimate_keyboard():
    keyboard = [[InlineKeyboardButton('1', callback_data='es1'), InlineKeyboardButton('2', callback_data='es2')],
                [InlineKeyboardButton('3', callback_data='es3'), InlineKeyboardButton('4', callback_data='es4')],
                [InlineKeyboardButton('5', callback_data='es5')]]
    return InlineKeyboardMarkup(keyboard)


def get_curator():
    actual_curator = curators_queue.pop(0)
    curators_queue.append(actual_curator)
    return actual_curator


# def get_actual_curator():

def update_pinned(update, context):
    cht = context.bot.getChat(update.message.chat.id)
    pndmsg = cht.pinned_message
    check_message_id = pndmsg.forward_from_message_id
    if update.message.forward_from_chat.id in curators.keys():
        for user_chat_id, user_question in user_questions.items():
            if user_question['curator_channel_message_id'] == check_message_id:
                user_questions[user_chat_id]['curator_chat_message_id'] = pndmsg.message_id
                user_questions[user_chat_id]['status'] = 2
                break
    else:
        for user_chat_id, user_question in user_questions.items():
            if user_question['main_channel_message_id'] == check_message_id:
                user_questions[user_chat_id]['main_chat_message_id'] = pndmsg.message_id
                user_questions[user_chat_id]['status'] = 2
                break


def handle_curator_message(update, context):
    reply_message_id = update.message.reply_to_message.message_id
    for user_chat_id, user_question in user_questions.items():
        if (user_question['curator_chat_message_id'] == reply_message_id or user_question[
            'main_chat_message_id'] == reply_message_id) and user_question['status'] <= 2:
            to_user = context.bot.copy_message(
                chat_id=user_chat_id,
                # reply_to_message_id=user_questions[user_chat_id]['main_chat_message_id'],
                message_id=update.message.message_id,
                from_chat_id=update.message.chat_id
            )

            if user_question['main_chat_message_id'] != reply_message_id:
                caption = 'Ответ куратора'
                if update.message.caption:
                    caption = 'Ответ куратора\n' + update.message.caption

                to_main_chat = context.bot.copy_message(
                    chat_id=main_chat,
                    reply_to_message_id=user_questions[user_chat_id]['main_chat_message_id'],
                    message_id=update.message.message_id,
                    from_chat_id=update.message.chat_id,
                    caption=caption
                )
                if update.message.text:
                    text = 'Ответ куратора: \n' + update.message.text
                    context.bot.editMessageText(
                        chat_id=main_chat,
                        message_id=to_main_chat.message_id,
                        text=text
                    )
            else:
                caption = 'Ответ методиста'
                if update.message.caption:
                    caption = 'Ответ методиста\n' + update.message.caption

                to_main_chat = context.bot.copy_message(
                    chat_id=curators[user_questions[user_chat_id]['curator_id']],
                    reply_to_message_id=user_questions[user_chat_id]['curator_chat_message_id'],
                    message_id=update.message.message_id,
                    from_chat_id=update.message.chat_id,
                    caption=caption
                )
                if update.message.text:
                    text = 'Ответ методиста: \n' + update.message.text
                    context.bot.editMessageText(
                        chat_id=curators[user_questions[user_chat_id]['curator_id']],
                        message_id=to_main_chat.message_id,
                        text=text
                    )


def first_submenu(update, context):
    custom_keyboard = [['Задать вопрос']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
    # bot.callback_query.message.reply_text("Спасибо за оценку", reply_markup=reply_markup)

    estimate_string = context.match.string
    estimate = int(re.sub("[^0-9]", "", estimate_string))

    user_chat_id = update.callback_query.message.chat_id

    if user_chat_id in user_questions.keys() and user_questions[user_chat_id]['status'] is not None and \
            user_questions[user_chat_id]['status'] == 3:

        update.callback_query.message.reply_text("Спасибо за оценку", reply_markup=reply_markup)
        user_questions[user_chat_id]['status'] = 4

        context.bot.send_message(
            chat_id=main_chat,
            text='Оценка пользователя ' + str(estimate) + " из 5",
            reply_to_message_id=user_questions[user_chat_id]['main_chat_message_id']
        )

        if estimate <= 3:
            update.callback_query.message.reply_text(
                "Расскажите пожалуйста подробнее, что вам не понравилось в работе куратора:", reply_markup=reply_markup)
        else:
            user_questions.pop(user_chat_id, None)

    elif user_questions[user_chat_id]['status'] == 4:
        update.callback_query.message.reply_text(
            "Оценка уже поставлена,\n Расскажите пожалуйста подробнее, что вам не понравилось в работе куратора:",
            reply_markup=reply_markup)
