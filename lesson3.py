from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from config import token
import sqlite3 

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

connect = sqlite3.connect("anketa.db")
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS anketa_bot(
               user_id INTEGER PRIMARY KEY ,
               full_name VARCHAR(255) NOT NULL,
               age INTEGER NOT NULL,
               email TEXT DEFAULT NULL,
               phone TEXT,
               experience INTEGER DEFAULT 0
)''')
connect.commit()

class ResumeState(StatesGroup):
    full_name = State()
    age = State()
    email = State()
    phone = State()
    experience = State()

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer("Привет")


@dp.message_handler(commands='resume')
async def start(message:types.Message):
    await ResumeState.full_name.set()
    await message.answer("Введите ваше полное имя: ")

@dp.message_handler(state=ResumeState.full_name)
async def full_name(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text

    await ResumeState.next()
    await message.answer("Введите ваш возраст:")

@dp.message_handler(state=ResumeState.age)
async def age(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    
    await ResumeState.next()
    await message.answer("Введите ваш email: ")


@dp.message_handler(state=ResumeState.email)
async def age(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
    
    await ResumeState.next()
    await message.answer("Введите ваш номер:")


@dp.message_handler(state=ResumeState.phone)
async def age(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    
    await ResumeState.next()
    await message.answer("Какой у вас стаж работы:")


@dp.message_handler(state=ResumeState.experience)
async def age(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['experience'] = message.text

    cursor.execute('''
INSERT OR REPLACE INTO anketa_bot (user_id, full_name, age, email, phone, experience) VALUES(?,?,?,?,?,?)'''
,(message.from_user.id ,data['full_name'], data['age'], data['email'], data['phone'], data['experience']))
    connect.commit()
    
    await message.answer("Мы сохранили ваши данные!")
    await state.finish()



    
executor.start_polling(dp)