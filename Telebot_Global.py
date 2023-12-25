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

    global database
    database = df.to_dict('records')
    global questions
    questions = df.columns.tolist()[1:]

    ask_question(call.message.chat.id, questions[0])


def ask_question(id, qst):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Да", callback_data="Yes")
    button2 = types.InlineKeyboardButton("Нет", callback_data="No")
    markup.row(button1, button2)
    bot.send_message(id, f"{qst}", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["Yes", "No"])
def callback_message(call):
    if call.data == "Yes":
        answer = True
    else:
        answer = False

    to_remove = []
    for d in database:
        if d[questions[0]] != answer:
            to_remove.append(d)

    for i in to_remove:
        database.remove(i)

    questions.pop(0)

    if len(database) == 1:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Начать новую игру", callback_data="start")
        markup.row(button1)
        bot.send_message(call.message.chat.id, "Вы загадали слово " + database[0]["name"], reply_markup=markup)
    elif len(database) == 0:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Начать новую игру", callback_data="start")
        markup.row(button1)
        bot.send_message(call.message.chat.id, "Не нашел такого слова в базе данных", reply_markup=markup)
    else:
        ask_question(call.message.chat.id, questions[0])


bot.polling(none_stop=True)
