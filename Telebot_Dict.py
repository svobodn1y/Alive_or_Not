import pandas as pd
import telebot
from telebot import types
import time
import openpyxl
import numpy as np
import os
import sys
import random

bot = telebot.TeleBot('6442849889:AAELPAMSRdASQ2s8f-Ta4VEovWwBOSNoC1M')

user_dict = {}


@bot.message_handler(commands=['start'])
def beginning(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Начать игру", callback_data="start")
    markup.add(button1)
    bot.send_message(message.chat.id, "Загадай слово, а Я попытаюсь его угадать.\nДля этого Я буду задавать вопросы. "
                                      "Начнем?".format(message.from_user), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'start')
def callback_message(call):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Да", callback_data="Alive")
    button2 = types.InlineKeyboardButton("Нет", callback_data="Thing")
    markup.row(button1, button2)
    bot.send_message(call.message.chat.id, "Это живое?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["Alive", "Thing"])
def callback_message(call):
    if call.data == "Alive":
        df = pd.read_excel("Alive.xlsx")
    else:
        df = pd.read_excel("Things.xlsx")

    database = df.to_dict('records')
    questions = df.columns.tolist()[1:]

    user_dict[f"{call.message.from_user.id}"] = [questions, database]

    ask_question(call.message.chat.id, user_dict[f"{call.message.from_user.id}"][0][0])


def ask_question(ind, qst):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Да", callback_data="Yes")
    button2 = types.InlineKeyboardButton("Нет", callback_data="No")
    markup.row(button1, button2)
    bot.send_message(ind, f"{qst}", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["Yes", "No"])
def callback_message(call):
    if call.data == "Yes":
        answer = True
    else:
        answer = False

    database = user_dict[f"{call.message.from_user.id}"][1]
    question = user_dict[f"{call.message.from_user.id}"][0][0]

    to_remove = []

    for d in database:
        if d[question] != answer:
            to_remove.append(d)

    for i in to_remove:
        (user_dict[f"{call.message.from_user.id}"][1]).remove(i)

    (user_dict[f"{call.message.from_user.id}"][0]).pop(0)

    if len(user_dict[f"{call.message.from_user.id}"][1]) == 1:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Начать новую игру", callback_data="start")
        markup.row(button1)
        bot.send_message(call.message.chat.id, "Вы загадали слово " + database[0]["name"], reply_markup=markup)
        del user_dict[f"{call.message.from_user.id}"]

    elif len(user_dict[f"{call.message.from_user.id}"][0]) == 0:
        final_questions(call.message.from_user.id, call.message.chat.id)

    elif len(user_dict[f"{call.message.from_user.id}"][1]) == 0:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Начать новую игру", callback_data="start")
        markup.row(button1)
        bot.send_message(call.message.chat.id, "Не нашел такого слова в базе данных", reply_markup=markup)
        del user_dict[f"{call.message.from_user.id}"]

    else:
        ask_question(call.message.chat.id, (user_dict[f"{call.message.from_user.id}"][0][0]))


def final_questions(user_id, chat_id):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Да", callback_data="Yep")
    button2 = types.InlineKeyboardButton("Нет", callback_data="Nop")
    markup.row(button1, button2)
    bot.send_message(chat_id, f"Это {user_dict[f'{user_id}'][1][0]['name']}?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["Yep", "Nop"])
def callback_message(call):
    if call.data == "Yep":
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Начать новую игру", callback_data="start")
        markup.row(button1)
        bot.send_message(call.message.chat.id, "Вы загадали слово " + user_dict[f"{call.message.from_user.id}"][1][0]["name"], reply_markup=markup)

        del user_dict[f"{call.message.from_user.id}"]

    elif call.data == "Nop" and len(user_dict[f'{call.message.from_user.id}'][1]) == 1:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Начать новую игру", callback_data="start")
        markup.row(button1)
        bot.send_message(call.message.chat.id, "Не нашел такого слова в базе данных", reply_markup=markup)

        del user_dict[f"{call.message.from_user.id}"]

    else:
        user_dict[f"{call.message.from_user.id}"][1].pop(0)
        final_questions(call.message.from_user.id, call.message.chat.id)


bot.polling(none_stop=True)
