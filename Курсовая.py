import telebot
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import random
import requests
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import json
from models import create_tables, Word, New_word, Client
from random import randint
from random import shuffle

login = str(input('Введите логин:'))
password = str(input('Введите пароль:'))
name_bd = str(input('Введите название базы данных:'))
DSN = f'postgresql+psycopg2://{login}:{password}@localhost:5432/{name_bd}'
engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()

create_tables(engine)

def load_db():
    with open ('База_данных_json.json', encoding='utf-8') as f:
        data = json.load(f)

    for record in data:
        model = {
            'word': Word,
            'new_word': New_word,
        }[record.get('model')]
        session.add(model(id=record.get('pk'), rus=record.get('rus'), en=record.get('en'), w_en_1=record.get('w_en_1'), w_en_2=record.get('w_en_2'), w_en_3=record.get('w_en_3')))
    session.commit()

load_db()

state_storage = StateMemoryStorage()
token_bot = input()
bot = telebot.TeleBot(token_bot)
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0

@bot.message_handler(commands=['start'])
def start_bot(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, 'Привет 👋 Давай попрактикуемся в английском языке.'
                         'Тренировки можешь проходить в удобном для себя темпе.'
                          'У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения.'
                          'Для этого воспрользуйся инструментами:'
                          'добавить слово ➕' 
                          'удалить слово 🔙'
                          'Ну что, начнём ⬇️')
            
@bot.message_handler(commands=['cards'])
def cards_bot(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
    marcup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    data = session.query(
        Word.rus, Word.en, Word.w_en_1, Word.w_en_2, Word.w_en_3
    ).select_from(Word)
    random = randint(1, 15)
    global nobber
    nobber = random
    pub = data.filter(Word.id == random).all()
    for rus, en, w_en_1, w_en_2, w_en_3 in pub:
        rus_word = rus
        target_word = en        
        other_word = [w_en_1, w_en_2, w_en_3]
    global buttons
    buttons = []
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    other_words_btns = [types.KeyboardButton(word) for word in other_word]
    buttons.extend(other_words_btns)
    shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    marcup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {rus_word}"
    bot.send_message(message.chat.id, greeting, reply_markup=marcup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = rus_word
        data['other_words'] = other_word

@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    cards_bot(message)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        print(data['target_word'])  # удалить из БД

@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    print(message.text)  # сохранить в БД

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")

    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    print('Bot is runung!')
    bot.polling()


