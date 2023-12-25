import pandas as pd
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class ClientState(StatesGroup):
    START_GAME = State()
    TYPE_SELECTED = State()
    ASKING_QUESTIONS = State()
    LOOP = State()


bot = Bot(token='6442849889:AAELPAMSRdASQ2s8f-Ta4VEovWwBOSNoC1M')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_proccess(message: types.Message, state: FSMContext) -> None:

    msg = "Загадай слово, а Я попытаюсь его угадать.\nДля этого Я буду задавать вопросы. Начнем?"
    msk_btn = KeyboardButton('Начать Игру')

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(msk_btn)

    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.START_GAME)


@dp.message_handler(state=ClientState.START_GAME)
async def choose_type_process(message: types.Message, state: FSMContext):

    alive_btn = KeyboardButton('Да')
    not_alive_btn = KeyboardButton('Нет')

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(alive_btn, not_alive_btn)

    await message.answer('Это живое?', reply_markup=markup)
    await state.set_state(ClientState.TYPE_SELECTED)


@dp.message_handler(state=ClientState.TYPE_SELECTED)
async def beginning_process(message: types.Message, state: FSMContext):

    user_msg = message.text
    if user_msg == 'Да':
        df = pd.read_excel("Alive.xlsx")
    else:
        df = pd.read_excel("Things.xlsx")

    database = df.to_dict('records')
    questions = df.columns.tolist()[1:]
    await state.update_data(DB=database)
    await state.update_data(QUEST=questions)

    button1 = KeyboardButton(text="Да", callback_data="ask")
    button2 = KeyboardButton(text="Нет", callback_data="ask")
    button3 = KeyboardButton(text="Пропустить вопрос")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(button1, button2)
    markup.row(button3)

    await message.answer(f"{questions[0]}", reply_markup=markup)
    await state.set_state(ClientState.ASKING_QUESTIONS)


@dp.message_handler(state=ClientState.ASKING_QUESTIONS)
async def asking_questions_process(message: types.Message, state: FSMContext):

    user_msg = message.text
    if user_msg == 'Да':
        answer = True
    elif user_msg == 'Нет':
        answer = False

    user_state_data = await state.get_data()
    to_remove = []
    database = user_state_data['DB']
    questions = user_state_data['QUEST']

    if user_msg != "Пропустить вопрос":
        for d in database:
            if d[questions[0]] != answer:
                to_remove.append(d)

        for i in to_remove:
            database.remove(i)

    questions.pop(0)

    if len(database) == 1:
        button = KeyboardButton('Начать новую игру')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button)

        await message.answer("Вы загадали слово " + database[0]["name"], reply_markup=markup)
        await state.set_state(ClientState.START_GAME)

    elif len(database) == 0:
        button = KeyboardButton('Начать новую игру')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button)

        await message.answer("Не нашел такого слова в базе данных😔", reply_markup=markup)
        await state.set_state(ClientState.START_GAME)

    elif len(questions) == 0:
        button1 = KeyboardButton(text="Да", callback_data="ask")
        button2 = KeyboardButton(text="Нет", callback_data="ask")

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button1, button2)

        await message.answer(f"Это {database[0]['name']}?", reply_markup=markup)
        await state.set_state(ClientState.LOOP)

    else:
        await state.update_data(DB=database)
        await state.update_data(QUEST=questions)

        button1 = KeyboardButton(text="Да")
        button2 = KeyboardButton(text="Нет")
        button3 = KeyboardButton(text="Пропустить вопрос")

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button1, button2)
        markup.row(button3)

        await message.answer(f"{questions[0]}", reply_markup=markup)


@dp.message_handler(state=ClientState.LOOP)
async def loop_process(message: types.Message, state: FSMContext):
    user_msg = message.text
    user_state_data = await state.get_data()

    database = user_state_data['DB']
    if user_msg == 'Да':
        button = KeyboardButton('Начать новую игру')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button)

        await message.answer("Вы загадали слово " + database[0]["name"], reply_markup=markup)
        await state.set_state(ClientState.START_GAME)

    elif len(database) == 1:
        button = KeyboardButton('Начать новую игру')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button)

        await message.answer("Не нашел такого слова в базе данных😔", reply_markup=markup)
        await state.set_state(ClientState.START_GAME)

    else:
        database.pop(0)
        await state.update_data(DB=database)

        button1 = KeyboardButton(text="Да")
        button2 = KeyboardButton(text="Нет")

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button1, button2)

        await message.answer(f"Это {database[0]['name']}?", reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
