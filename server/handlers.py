import json

from telebot import types

from server import bot, db

import server.models as model
import server.searching as search
from server.constants import *
from server.localization import *


LANGUAGE_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                            one_time_keyboard=True)
LANGUAGE_MARKUP.add(types.KeyboardButton(KZ_CHOICE),
                    types.KeyboardButton(RU_CHOICE),
                    types.KeyboardButton(EN_CHOICE))


SEARCH_ACTION = model.Action(ActionCode.SEARCH).to_json()
CATEGORIES_ACTION = model.Action(ActionCode.CATEGORIES).to_json()
LANGUAGE_ACTION = model.Action(ActionCode.LANGUAGE).to_json()
MAIN_MENU_ACTION = model.Action(ActionCode.MAIN_MENU).to_json()


def update_commands(chat_id, language):
    command_list = []
    for i, command in enumerate(COMMANDS):
        command_list.append(
            types.BotCommand(command, COMMAND_DESCRIPTIONS[language][i]))
    bot.set_my_commands(command_list,
                        types.BotCommandScopeChat(chat_id))


def get_user(message):
    if message.chat.type != 'private':
        return

    user = model.User.query.get(message.chat.id)
    if user is None:
        user = model.User(message.chat.id)
        db.session.add(user)
        db.session.commit()
    return user


def save_user(user):
    db.session.merge(user)
    db.session.commit()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type != 'private':
        return

    bot.send_message(message.chat.id, LANGUAGE_CHOICE_TEXT, reply_markup=LANGUAGE_MARKUP)
    bot.register_next_step_handler(message, process_language_step)


@bot.message_handler(commands=['language'])
def process_language_step(message):
    user = get_user(message)
    if message.text == KZ_CHOICE:
        user.language = KZ
    elif message.text == RU_CHOICE:
        user.language = RU
    elif message.text == EN_CHOICE:
        user.language = EN
    else:
        bot.send_message(message.chat.id, LANGUAGE_CHOICE_TEXT, reply_markup=LANGUAGE_MARKUP)
        bot.register_next_step_handler(message, process_language_step)
        return

    user.query = ""
    save_user(user)

    update_commands(message.chat.id, user.language)

    remove_markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, WELCOME[user.language], reply_markup=remove_markup)

    on_main_menu(message)


@bot.message_handler(commands=['mainmenu'])
def on_main_menu(message):
    user = get_user(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(SEARCH[user.language], callback_data=SEARCH_ACTION))
    markup.add(types.InlineKeyboardButton(SEARCH_BY_CATEGORY[user.language], callback_data=CATEGORIES_ACTION))
    markup.add(types.InlineKeyboardButton(CHANGE_LANGUAGE[user.language], callback_data=LANGUAGE_ACTION))
    markup.add(types.InlineKeyboardButton(TECH_SUPPORT[user.language], url=THY_TECH_SUPPORT_GUY))
    bot.send_message(message.chat.id, ABOUT[user.language], reply_markup=markup)


@bot.message_handler(commands=['search'])
def on_search(message):
    user = get_user(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(BACK_TO_MAIN_MENU[user.language], callback_data=MAIN_MENU_ACTION))
    message_text = f'<b>{ENTER_BOOK_NAME[user.language]}</b>'
    bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode='HTML')


@bot.message_handler(commands=['categories'])
def on_categories_search(message):
    user = get_user(message)
    markup = types.InlineKeyboardMarkup()
    for i in range(len(EXCEL_TABLES)):
        json_action = model.Action(ActionCode.CATEGORY_SELECT, [i, 0, 10]).to_json()
        markup.add(types.InlineKeyboardButton(CATEGORIES[user.language][i], callback_data=json_action))
    bot.send_message(message.chat.id, SELECT_CATEGORY[user.language], reply_markup=markup)


def on_category_select(message, category_index):
    user = get_user(message)
    user.query = "category:{}".format(category_index)
    save_user(user)
    search_and_display_books(message, [0, 10])


def search_and_display_books(message, args, on_bound=None):
    user = get_user(message)
    query = user.query
    range_start, range_end = args

    if query.startswith("category:"):
        category_index = int(query[9:])
        results = search.books_by_category(category_index)
        category_name = CATEGORIES[user.language][category_index]
        message_text = f'<b>{BOOK_CATEGORY[user.language]}</b><i>{category_name}</i>\n'
    else:
        results = search.books_by_query(query)
        message_text = f'<b>{QUERY[user.language]}</b><i>{query}</i>\n'

    if on_bound is not None and (range_start < 0 or range_end > len(results) + 10 - len(results) % 10):
        on_bound()
        return

    range_start = max(0, range_end - (range_end % 10 if range_end % 10 != 0 else 10))
    range_end = min(len(results), range_start + 10)
    message_text += search.query_result_to_string(range_start, range_end, results)

    prev_page_action = model.Action(ActionCode.PREV_PAGE, [range_start - 10, range_end - 10]).to_json()
    next_page_action = model.Action(ActionCode.NEXT_PAGE, [range_start + 10, range_end + 10]).to_json()

    markup = types.InlineKeyboardMarkup()
    buttons = []

    for i in range(range_start, range_end):
        if i >= len(results):
            break
        book_action = model.Action(ActionCode.BOOK, args=[results[i].book_id]).to_json()
        buttons.append(types.InlineKeyboardButton(results[i].book_id, callback_data=book_action))

    markup.add(*buttons, row_width=5)
    markup.add(
        types.InlineKeyboardButton("<<<", callback_data=prev_page_action),
        types.InlineKeyboardButton(BACK_TO_MAIN_MENU[user.language], callback_data=MAIN_MENU_ACTION),
        types.InlineKeyboardButton(">>>", callback_data=next_page_action)
    )

    bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode='HTML')
    bot.delete_message(message.chat.id, message.message_id)


def on_book_checkout(call, book_id):
    user = get_user(call.message)
    query = user.query
    results = search.books_by_category(int(query[9:])) if query.startswith("category:") \
        else search.books_by_query(query)
    book_entry = results[book_id - 1].to_string(user.language)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(FIND_OTHER_BOOK[user.language], callback_data=SEARCH_ACTION))
    bot.send_message(call.message.chat.id, book_entry, reply_markup=markup, parse_mode='HTML')


@bot.message_handler(func=lambda message: True)
def process_search_step(message):
    user = get_user(message)

    if len(message.text) > 64:
        bot.send_message(message.chat.id, QUERY_TOO_LONG[user.language])
        return

    user.query = message.text
    save_user(user)
    results = search.books_by_query(message.text)

    if len(results) == 0:
        bot.send_message(message.chat.id, BOOK_NOT_FOUND[user.language])
        return

    search_and_display_books(message, [0, 10])


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    json_action = json.loads(call.data)
    if not call.message:
        return
    if json_action["name"] == ActionCode.SEARCH:
        on_search(call.message)
    elif json_action["name"] == ActionCode.NEXT_PAGE:
        user = get_user(call.message)
        search_and_display_books(call, json_action["args"], lambda: bot.answer_callback_query(
            call.id, YOU_REACHED_THE_END[user.language]))
        return
    elif json_action["name"] == ActionCode.PREV_PAGE:
        user = get_user(call.message)
        search_and_display_books(call, json_action["args"], lambda: bot.answer_callback_query(
            call.id, YOU_REACHED_THE_START[user.language]))
        return
    elif json_action["name"] == ActionCode.BOOK:
        on_book_checkout(call, json_action["args"][0])
    elif json_action["name"] == ActionCode.CATEGORIES:
        on_categories_search(call.message)
    elif json_action["name"] == ActionCode.CATEGORY_SELECT:
        on_category_select(call.message, json_action["args"][0])
    elif json_action["name"] == ActionCode.LANGUAGE:
        process_language_step(call.message)
    elif json_action["name"] == ActionCode.MAIN_MENU:
        on_main_menu(call.message)

    bot.answer_callback_query(call.id)
