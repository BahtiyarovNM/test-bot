import os
import re

from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ForceReply, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from settings import WELCOME_MESSAGE, TELEGRAM_SUPPORT_CHAT_ID, TELEGRAM_SUPERCHAT_ID

msgId2chatId = dict()
# (forward_from) connect message_id from chat to chat_id user's chat

lastMsg = dict()
# last message in SUPERCHAT for this user's question. Connect users and last message for their chat

# from functools import wraps

is_opened_question = dict()
g_chat_id = 0
g_message = None

is_estimated = dict()
is_estimate_described = dict()


# def restricted(func):
#     @wraps(func)
#     def wrapped(update, context, *args, **kwargs):
#         user_id = update.effective_user.id
#         new_chat_id = update.message.chat_id
#         ioq = is_opened_question.get(new_chat_id)
#         if  ioq == None or ioq <= 0:
#             print("Unauthorized access denied for {}.".format(user_id))
#             return
#         return func(update, context, *args, **kwargs)
#     return wrapped

def logIT():
    print('is_opened_question')
    print(is_opened_question)
    print('msgId2chatId')
    print(msgId2chatId)
    print('lastMsg')
    print(lastMsg)
    print('g_chat_id')
    print(g_chat_id)


#     print('g_message')
#     print(g_message)

def start(update, context):
    #     update.message.reply_text(WELCOME_MESSAGE, reply_markup=ForceReply(force_reply=True, input_field_placeholder = "Задайте свой вопрос"))
    print('/start')
    logIT()
    custom_keyboard = [['Задать вопрос']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        'Добро пожаловать в чат поддержки NSA. Чтобы задать вопрос выберите "Задать вопрос"',
        reply_markup=reply_markup)


#     buttons = [
#         [
#             InlineKeyboardButton("Задать Вопрос", callback_data="Задать Вопрос")
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(buttons)

#     update.message.reply_text(
#         WELCOME_MESSAGE,
#         reply_markup=reply_markup,
#         quote=True
#     )    

#     user_info = update.message.from_user.to_dict()
#     context.bot.send_message(
#         chat_id=TELEGRAM_SUPPORT_CHAT_ID,
#         text=f"""
# 📞 Connected {user_info}.
#         """
#     )

def new_question(update, context):
    #     callback_query = update.callback_query
    #     callback_query.answer()
    #     text = callback_query.message.text
    #     data = callback_query.data
    new_chat_id = update.message.from_user.id
    ioq = is_opened_question.get(new_chat_id)
    is_estimate_described[new_chat_id] = True
    if ioq == None or ioq <= 0:

        print('new Q')
        custom_keyboard = [['Вопрос решен']]  # custom_keyboard,
        reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text("Опишите свой вопрос и нажмите отправить", reply_markup=reply_markup)
        #     Спасибо за вопрос. В ближайшее время Вам ответит первый из освободившихся специалистов.
        user_info = update.message.from_user.to_dict()

        #         global is_opened_question
        is_opened_question[new_chat_id] = 3
    elif ioq > 0:
        custom_keyboard = [['Вопрос решен']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text(
            'У вас уже открыт вопрос. Опишите свой вопрос и нажмите отправить',
            reply_markup=reply_markup)
        return
    logIT()


def update_pinned(update, context):  ##############
    #     new_user_id = user_info['id']
    global g_chat_id
    new_chat_id = g_chat_id
    cht = context.bot.getChat(TELEGRAM_SUPERCHAT_ID)
    pndmsg = cht.pinned_message
    check_message_id = pndmsg.forward_from_message_id  # forward_from.chat_id # forward_from_chat.id
    global g_message
    check_g_message_id = g_message.message_id
    global is_opened_question  #
    is_opened_question[new_chat_id] = 2  #
    is_estimated[new_chat_id] = False
    print("pin", check_message_id, check_g_message_id)
    new_message_id = pndmsg.message_id  # new_message.message_id ########### lazha # test
    if check_g_message_id == check_message_id:
        msgId2chatId[new_message_id] = new_chat_id
        lastMsg[new_chat_id] = new_message_id
        print("pin OK")


#     update.message.forward(chat_id=TELEGRAM_SUPPORT_CHAT_ID)
#     callback_query

def close_problem(update, context):
    print('Close problem')
    new_chat_id = update.message.from_user.id  #
    ioq = is_opened_question.get(new_chat_id)
    print(ioq)
    if ioq == 2:
        custom_keyboard = [['Задать вопрос']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        reply_markup = on_end_estimate_keyboard()
        update.message.reply_text("Вопрос закрыт, поставьте оценку", reply_markup=reply_markup)
        new_chat_id = update.message.chat_id
        last_message_id = lastMsg[new_chat_id]
        #         global is_opened_question
        is_opened_question[new_chat_id] = -1
        #     is_opened_question.pop(new_chat_id)   # add it later
        context.bot.send_message(
            chat_id=TELEGRAM_SUPERCHAT_ID,
            text='Вопрос закрыт пользователем',
            reply_to_message_id=last_message_id
        )

        is_opened_question.pop(new_chat_id, None)
    elif ioq == 3:
        custom_keyboard = [['Вопрос решен']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text("Вы не задали свой вопрос", reply_markup=reply_markup)
    elif ioq == None:
        custom_keyboard = [['Задать вопрос']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text("Вопрос закрыт", reply_markup=reply_markup)
def forward_to_chat(update, context):
    """{ 
        'message_id': 5, 
        'date': 1605106546, 
        'chat': {'id': 49820636, 'type': 'private', 'username': 'danokhlopkov', 'first_name': 'Daniil', 'last_name': 'Okhlopkov'}, 
        'text': 'TEST QOO', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 
        'from': {'id': 49820636, 'first_name': 'Daniil', 'is_bot': False, 'last_name': 'Okhlopkov', 'username': 'danokhlopkov', 'language_code': 'en'}
    }"""
    #   user_chat_id = update.message.reply_to_message.forward_from.id
    #     c_id = update.message.chat_id
    #     m_id = context.bot.copy_message(
    #         message_id=update.message.message_id,
    #         chat_id=TELEGRAM_SUPERCHAT_ID,
    #         from_chat_id=c_id
    # #         update.message.chat_id
    #     )
    #     msgId2chatId[m_id] = c_id
    print('fwd2chat')
    new_chat_id = update.message.chat_id
    custom_keyboard = [['Задать вопрос']]
    reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
    ioq = is_opened_question.get(new_chat_id)
    if is_estimate_described.get(new_chat_id) != None and not is_estimate_described[new_chat_id]:
        is_estimate_described[new_chat_id] = True

        update.message.reply_text(
            'Спасибо за ответ',
            reply_markup=reply_markup)
        return
    if ioq == None or ioq <= 0:
        update.message.reply_text(
            'Чтобы задать вопрос нажмите кнопку "Задать вопрос"',
            reply_markup=reply_markup)
        return
    elif ioq == 1:
        custom_keyboard = [['Вопрос решен']]
        reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text(
            'Сообщение не доставлено. Задайте вопрос повторно.',
            reply_markup=reply_markup)
        return
    elif ioq == 2:
        #         update.message.forward(chat_id=TELEGRAM_SUPERCHAT_ID)
        #         new_user_id = update.message.from.id

        #         cht = context.bot.getChat(TELEGRAM_SUPERCHAT_ID)
        #         pndmsg = cht.pinned_message
        last_message_id = lastMsg[new_chat_id]
        # print(lastMsg)
        # print(update.message)
        # context.bot.send_message()
        #         new_message = context.bot.send_message(
        #             chat_id=TELEGRAM_SUPERCHAT_ID,
        #             # text=update.message.text,
        #             reply_to_message_id=last_message_id,
        #             msg=update.message
        # #             reply_to_message_id=pndmsg.message_id
        #         )
        # new_message = update.message.forward(chat_id=TELEGRAM_SUPERCHAT_ID)
        #         new_chat_id = update.message.chat_id
        #         new_user_id = user_info['id']
        print(lastMsg)
        new_message = context.bot.copy_message(
            chat_id=TELEGRAM_SUPERCHAT_ID,
            reply_to_message_id=last_message_id,
            message_id=update.message.message_id,
            from_chat_id=update.message.chat_id
        )
        new_message_id = new_message.message_id
        msgId2chatId[new_message_id] = new_chat_id
        # lastMsg[new_chat_id] = new_message_id
        print("fwd2chat ", new_chat_id, "OK")
    elif ioq == 3:

        # new_message = context.bot.send_message(
        #     chat_id=TELEGRAM_SUPPORT_CHAT_ID,
        #     text=f"""Новый вопрос от пользователя {user_info}."""
        #     #       как отправить сам вопрос пока хз, есть вариант убрать кнопку задать вопрос
        # )
        new_message = context.bot.copy_message(
            chat_id=TELEGRAM_SUPPORT_CHAT_ID,
            # reply_to_message_id=last_message_id,
            message_id=update.message.message_id,
            from_chat_id=update.message.chat_id
        )
        global g_chat_id
        g_chat_id = new_chat_id = update.message.chat_id
        global g_message
        g_message = new_message
        is_opened_question[new_chat_id] = 3


def forward_to_user(update, context):
    """{
        'message_id': 10, 'date': 1605106662, 
        'chat': {'id': -484179205, 'type': 'group', 'title': '☎️ SUPPORT CHAT', 'all_members_are_administrators': True}, 
        'reply_to_message': {
            'message_id': 9, 'date': 1605106659, 
            'chat': {'id': -484179205, 'type': 'group', 'title': '☎️ SUPPORT CHAT', 'all_members_are_administrators': True}, 
            'forward_from': {'id': 49820636, 'first_name': 'Daniil', 'is_bot': False, 'last_name': 'Okhlopkov', 'danokhlopkov': 'okhlopkov', 'language_code': 'en'}, 
            'forward_date': 1605106658, 
            'text': 'g', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 
            'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 
            'from': {'id': 1440913096, 'first_name': 'SUPPORT', 'is_bot': True, 'username': 'lolkek'}
        }, 
        'text': 'ggg', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 
        'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 
        'from': {'id': 49820636, 'first_name': 'Daniil', 'is_bot': False, 'last_name': 'Okhlopkov', 'username': 'danokhlopkov', 'language_code': 'en'}
    }"""
    print('fwd2user')
    new_message_id = update.message.reply_to_message.message_id
    new_chat_id = user_chat_id = msgId2chatId[new_message_id]
    ioq = is_opened_question.get(new_chat_id)

    if ioq == None or ioq <= 0:
        update.message.reply_text('Вопрос закрыт пользователем')
        return
    elif ioq == 1:
        custom_keyboard = [['Вопрос решен']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text(
            'Сообщение не доставлено. Задайте вопрос повторно.',
            reply_markup=reply_markup)
        return
    elif ioq == 2:
        #     user_chat_id = update.message.reply_to_message.forward_from.id
        #         new_message =
        #         update.message.forward(chat_id=user_chat_id)

        last_message_id = lastMsg[new_chat_id]

        new_message = context.bot.copy_message(
            chat_id=user_chat_id,
            # reply_to_message_id=last_message_id,
            message_id=update.message.message_id,
            from_chat_id=update.message.chat_id
        )
        #         new_chat_id = update.message.reply_to_message.chat_id #
        new_message_id = new_message.message_id
        #         new_message_id = new_message.message_id
        msgId2chatId[new_message_id] = new_chat_id
        # lastMsg[new_chat_id] = new_message_id
        print("fwd2user ", new_chat_id, "OK")


#     context.bot.copy_message(
#         message_id=update.message.message_id,
#         chat_id=user_chat_id,
#         from_chat_id=update.message.chat_id
#     )

# def forward_to_user(update, context):
#     user_chat_id = update.channel_post.reply_to_message.forward_from.id
#     context.bot.copy_message(
#         message_id=update.channel_post.message_id,
#         chat_id=user_chat_id,
#         from_chat_id=update.channel_post.chat_id
#     )

def setup_dispatcher(dp):
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('^Задать вопрос$'), new_question))
    dp.add_handler(MessageHandler(Filters.regex('^Вопрос решен$'), close_problem))
    # dp.add_handler(CommandHandler('problem_closed', close_problem))
    dp.add_handler(CommandHandler('stop', close_problem))
    #     dp.add_handler(CallbackQueryHandler(new_question))
    #     dp.add_handler(MessageHandler(Filters. 'ask_qustion', new_question))
    dp.add_handler(MessageHandler(Filters.chat_type.private, forward_to_chat))
    dp.add_handler(MessageHandler(Filters.chat(TELEGRAM_SUPERCHAT_ID) & Filters.reply, forward_to_user))
    dp.add_handler(
        MessageHandler(Filters.chat(TELEGRAM_SUPERCHAT_ID) & Filters.forwarded_from(chat_id=TELEGRAM_SUPPORT_CHAT_ID),
                       update_pinned))
    dp.add_handler(CallbackQueryHandler(first_submenu,
                                        pattern='^.*es.*$'))
    return dp


# linked_chat_id
def on_end_estimate_keyboard():
    keyboard = [[InlineKeyboardButton('1', callback_data='es1'), InlineKeyboardButton('2', callback_data='es2')],
                [InlineKeyboardButton('3', callback_data='es3'), InlineKeyboardButton('4', callback_data='es4')],
                [InlineKeyboardButton('5', callback_data='es5')]]
    return InlineKeyboardMarkup(keyboard)


def first_submenu(bot, update):
    custom_keyboard = [['Задать вопрос']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
    # bot.callback_query.message.reply_text("Спасибо за оценку", reply_markup=reply_markup)

    estimate_string = update.match.string
    estimate = int(re.sub("[^0-9]", "", estimate_string))

    if is_estimated.get(bot.callback_query.message.chat_id) != None and not is_estimated[
        bot.callback_query.message.chat_id]:
        print(estimate)
        bot.callback_query.message.reply_text("Спасибо за оценку", reply_markup=reply_markup)
        is_estimated[bot.callback_query.message.chat_id] = True
        if estimate <= 3:
            bot.callback_query.message.reply_text(
                "Расскажите пожалуйста подробнее, что вам не понравилось в работе куратора:", reply_markup=reply_markup)
            is_estimate_described[bot.callback_query.message.chat_id] = False
    else:
        bot.callback_query.message.reply_text("Оценка уже поставлена", reply_markup=reply_markup)
