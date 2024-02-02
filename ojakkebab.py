from aiogram import Bot, Dispatcher, types, executor
import sqlite3
import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime

storage = MemoryStorage()

bot = Bot(token='6683291704:AAF8d9yeP5eDj-ChMMtBP2ZOPO1lorzbU-Q')
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

connect = sqlite3.connect("ojakkebab.db")
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS accounts(
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    data_joined DATETIME
    )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    phone INTEGER,
    title TEXT,
    adres TEXT
    )''')

connect.commit()

class Order(StatesGroup):
    name = State()
    phone = State()
    title = State()
    adres = State()

start_buutons = [
    types.KeyboardButton("Меню"),
    types.KeyboardButton("О нас"),
    types.KeyboardButton("Адрес"),
    types.KeyboardButton("Заказать еду")
]

start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_buutons)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer(f" {message.from_user.full_name}, добро пожаловать в Ожак Кебаб!", reply_markup=start_keyboard)

@dp.message_handler(text='Меню')
async def menu(message:types.Message):
    await message.reply("Вот наше меню:")
    await message.answer('https://nambafood.kg/ojak-kebap')

@dp.message_handler(text='О нас')
async def about_us(message:types.Message):
    await message.reply("Более подробнее о нас вы можете прочитать тут:")
    await message.answer('https://ocak.uds.app/c/about')
    
@dp.message_handler(text='Адрес')
async def adres(message:types.Message):
    await message.answer("ул. Исы Ахунбаева 97а")
    await message.answer_location(42.84331569978354, 74.60981772293441)

@dp.message_handler(text='Заказать еду')
async def zakaz(message:types.Message):
    await Order.name.set()
    await message.reply("Введите ваше имя:")
    
@dp.message_handler(state=Order.name)
async def get_phone(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply("Теперь введите свой номер:")
    await Order.next()
        
@dp.message_handler(state=Order.phone)
async def get_title(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = int(message.text)
    await message.reply("Теперь введите то, что хотите заказать:")
    await Order.next()

@dp.message_handler(state=Order.title)
async def get_adres(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await message.reply("Теперь введите свой адрес:")
    await Order.next()
        
@dp.message_handler(state=Order.adres)
async def process_order(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['adres'] = message.text

    cursor.execute('''INSERT INTO accounts (user_id, username, first_name, last_name, data_joined) 
                      VALUES (?, ?, ?, ?,?)''',
                   (message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, datetime.now()))

    cursor.execute('''INSERT INTO orders (name, phone, title, adres) 
                      VALUES (?, ?, ?, ?)''', 
                   (data['name'], data['phone'], data['title'], data['adres']))

    connect.commit()

    await message.answer("Анкета на заказ принята!")
    await state.finish()

executor.start_polling(dp, skip_updates=True)