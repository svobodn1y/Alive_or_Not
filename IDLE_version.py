import pandas as pd
import random
import telebot
from telebot import types
import openpyxl
import numpy as np

ans = input("Это живое?(y,n)")

if ans == "y":
    df = pd.read_excel("Alive.xlsx")
else:
    df = pd.read_excel("Things.xlsx")

database = df.to_dict('records')


def take_chance(answer, property):
    if answer == "y":
        answer = True
    else:
        answer = False

    to_remove = []
    for d in database:
        if d[property] != answer:
            to_remove.append(d)

    for i in to_remove:
        database.remove(i)

    if len(database) == 0:
        print("Не нашел такого слова в базе данных")

    elif len(database) == 1:
        print("Вы загадали слово " + database[0]["name"])


DB = df.columns.tolist()[1:]

DB = sorted(DB, key=lambda x: random.random())

for i in DB:
    if len(database) == 0:
        break
    ans = input(f"{i}(y,n)")
    take_chance(ans, i)
    if len(database) == 1:
        break
    if i == DB[-1]:
        for j in range(len(database)):
            ans = input(f"Это {database[j]['name']}?(y,n)")
            if ans == "y":
                print("Вы загадали слово " + database[j]["name"])
                break
            elif (j == len(database) - 1) and ans == "n":
                print("Не нашел такого слова в базе данных")
                break
