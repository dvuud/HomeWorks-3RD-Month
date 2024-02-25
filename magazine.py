import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from config import token
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import time
from aiogram.dispatcher.filters.state import State, StatesGroup

with sqlite3.connect("magazine.db") as connection:
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        user_id TEXT,
        full_name VARCHAR(255), 
        id_passport INTEGER,                   
        age INTEGER,
        password TEXT,
        data_joined DATETIME      
    );
    """)
    cursor.connection.commit()
    
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

class StateUser(StatesGroup):
    full_name = State()
    id_passport = State()
    password = State()
    age = State()

buttons = [
    types.KeyboardButton("Каталог товаров"),
    types.KeyboardButton("Корзина"),
    types.KeyboardButton("Оформить заказ"),
    types.KeyboardButton("Часто задаваемые вопросы"),
    types.KeyboardButton("Назад")
]

start_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    user_id = message.from_user.id

    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user = cursor.fetchone()
    cursor.connection.commit()


    if user is not None:
        await message.answer("Добро пожаловать в магазин техники!\n"
                                 "Здесь вы можете приобрести товар по очень выгодным ценам!", reply_markup=start_buttons)
    else:
        await message.answer(f"{message.from_user.full_name} добро пожаловать в магазин техники!\n"
"Здесь вы можете купить товар по приемлимой цене, а также у нас хороший и широкий выбор техники.\n"
"Но перед этим давайте зарегистрируемся!")

        await message.answer("Введите полное имя?")
        await StateUser.full_name.set()

@dp.message_handler(state=StateUser.full_name)
async def full_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['full_name'] = message.text

        await StateUser.id_passport.set()
        await message.answer("Хорошо, теперь ваш паспорт айди?")
    except Exception as e:
        logging.error(f"Error in full_name handler: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз или отмените операцию.")

@dp.message_handler(state=StateUser.id_passport)
async def passport(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['id_passport'] = message.text

        await StateUser.password.set()
        await message.answer("Отлично, ваш пароль")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный номер паспорта.")
    except Exception as e:
        logging.error(f"Error in id_passport handler: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз или отмените операцию.")
        
@dp.message_handler(state=StateUser.password)
async def passport(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['password'] = message.text

        await StateUser.age.set()
        await message.answer("Отлично, ваш возраст?")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный пароль")
    except Exception as e:
        logging.error(f"Error in password handler: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз или отмените операцию.")

@dp.message_handler(state=StateUser.age)
async def age(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['age'] = int(message.text)
            
        # Сохраняем все в базу данных
        cursor.execute(
            '''INSERT INTO users (user_id, full_name, id_passport, password, age, data_joined) 
            VALUES (?,?,?,?,?,?)''',
            (message.from_user.id, data['full_name'], data['id_passport'], data['password'], data['age'], time.time())
        )
        connection.commit()
        await state.finish()
        await message.answer("Регистрация прошла успешно!", reply_markup=start_buttons)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст.")
    except Exception as e:
        logging.error(f"Error in age handler: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз или отмените операцию.")

        
butttons = [
    types.KeyboardButton('Acer'),
    types.KeyboardButton('Asus'),
    types.KeyboardButton('Huawei'),
    types.KeyboardButton('Apple'),
    types.KeyboardButton("Назад")
    
]

start_butttons = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*butttons)

in_buttons = [
    types.InlineKeyboardButton("Добавить в корзину")
]

start_inbuttons = types.InlineKeyboardMarkup().add(*in_buttons)

cursor.execute('''CREATE TABLE IF NOT EXISTS catalog(
    id INTEGER PRIMARY KEY,
    name TEXT,
    price TEXT,
    img TEXT
    )''')    
cursor.connection.commit()


@dp.message_handler(text='Каталог товаров')
async def start(message: types.Message):
   await message.answer("Ниже есть кнопки по которым вы можете выбрать себе свой товар!", reply_markup=start_butttons)
    
@dp.message_handler(text='Acer')
async def start(message:types.Message):
    await message.answer("Топ ноутбуков от фирмы Acer в магазине Barmak:")
    url = 'https://barmak.store/category/Acer/'
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'lxml')

    all_laptops_name = soup.find_all('div', class_ = "tp-product-tag-2")
    all_laptops_price = soup.find_all('span', class_ = "tp-product-price-2 new-price")
    all_laptops_images = soup.find_all('div', class_ ="tp-product-thumb-2 p-relative z-index-1 fix w-img")


    for name, price, image in zip(all_laptops_name, all_laptops_price, all_laptops_images):
        await message.answer(f"{name.text} - {price.text} ", reply_markup=start_inbuttons)
        await message.answer_photo(image)
        
        cursor.execute('''INSERT INTO catalog (name, price, img) VALUES (?,?,?)''',
                  name, price, image)
        cursor.connection.commit()


@dp.message_handler(text='Asus')
async def start(message:types.Message):
    await message.answer("Топ ноутбуков от фирмы Asus в магазине Barmak:")
    url = 'https://barmak.store/category/Asus/'
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'lxml')

    all_laptops_name = soup.find_all('div', class_ = "tp-product-tag-2")
    all_laptops_price = soup.find_all('span', class_ = "tp-product-price-2 new-price")
    all_laptops_images = soup.find_all('div', class_ ="tp-product-thumb-2 p-relative z-index-1 fix w-img")

    for name, price, image in zip(all_laptops_name, all_laptops_price, all_laptops_images):
        await message.answer(f"{name.text} - {price.text}", reply_markup=start_inbuttons)
        await message.answer_photo(image)
        
        cursor.execute('''INSERT INTO catalog (name, price, img) VALUES (?,?,?)''',
                   name, price, image)
        cursor.connection.commit()

    
@dp.message_handler(text='Huawei')
async def start(message:types.Message):
    await message.answer("Топ ноутбуков от фирмы Huawei в магазине Barmak:")
    url = 'https://barmak.store/category/Huawei/'
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'lxml')

    all_laptops_name = soup.find_all('div', class_ = "tp-product-tag-2")
    all_laptops_price = soup.find_all('span', class_ = "tp-product-price-2 new-price")
    all_laptops_images = soup.find_all('div', class_ ="tp-product-thumb-2 p-relative z-index-1 fix w-img")

    for name, price, image in zip(all_laptops_name, all_laptops_price, all_laptops_images):
        await message.answer_photo(f"{name.text} - {price.text}", reply_markup=start_inbuttons)  
        await message.answer_photo(image)
        
        cursor.execute('''INSERT INTO catalog (name, price, img) VALUES (?,?,?)''',
                   name, price, image)
        cursor.connection.commit()

        
@dp.message_handler(text='Apple')
async def start(message:types.Message):
    await message.answer("Топ ноутбуков от фирмы Apple в магазине Barmak:")
    url = 'https://barmak.store/category/Apple/'
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'lxml')

    all_laptops_name = soup.find_all('div', class_ = "tp-product-tag-2")
    all_laptops_price = soup.find_all('span', class_ = "tp-product-price-2 new-price")
    all_laptops_images = soup.find_all('div', class_ ="tp-product-thumb-2 p-relative z-index-1 fix w-img")

    for name, price, image in zip(all_laptops_name, all_laptops_price, all_laptops_images):
        await message.answer(f"{name.text} - {price.text}", reply_markup=start_inbuttons)
        await message.answer_photo(image)  
        
    cursor.execute('''INSERT INTO catalog (name, price, img) VALUES (?,?,?)''',
                   name, price, image)
    cursor.connection.commit()

@dp.message_handler(text='Назад')
async def back(message:types.Message):
    await start(message)  
    
user_selections = {}

@dp.callback_query_handler(lambda c: c.data.startswith('Добавить в корзину'))
async def add_item_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item_id = int(callback_query.data.split('_')[2])

    if user_id not in user_selections:
        user_selections[user_id] = [] 

    if item_id not in user_selections[user_id]:
        user_selections[user_id].append(item_id)
        await bot.answer_callback_query(callback_query.id, text="Товар добавлен в корзину.")
    else:
        await bot.answer_callback_query(callback_query.id, text="Товар уже в корзине.")

korzina_buttons = [
    types.KeyboardButton("Добавить"),
    types.KeyboardButton("Удалить"),
    types.KeyboardButton("Просмотр корзины"),
    types.KeyboardButton("Назад")
]

start_korzina_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*korzina_buttons)

user_items = {}


@dp.message_handler(text='Корзина')
async def start(message:types.Message):
    user_id = message.from_user.id
    user_items[user_id] = {}
    await message.answer("Привет это ваша корзина с низу есть нужные для вас кнопки!")

@dp.message_handler(text='Добавить')
async def a(message:types.Message):
    user_id = message.from_user.id
    item_name = message.text
    
    if item_name:
        user_items[user_id].append(item_name)
        await message.reply(f"Товар '{item_name}' добавлен в корзину.")
    else:
        await message.reply("""Нажмите на кнопку 'Добавить' Название товара.""")
        
@dp.message_handler(text='Удалить')
async def remove(message:types.Message):
    user_id = message.from_user.id
    item_name = message.text
    
    if item_name:
        user_items[user_id].remove(item_name)
        await message.reply(f"Товар '{item_name}' удален в корзину.")
    else:
        await message.reply("""Нажмите на кнопку 'Удалить' Название товара.""")
        
@dp.message_handler(text='Просмотр корзины')
async def view(message:types.Message):
    user_id = message.from_user.id
    items_content = "\n".join(items_content[user_id]) if items_content[user_id] else "Корзина пуста."
    await message.reply(f"Содержимое корзины:\n{items_content}")
    
@dp.message_handler(text='Назад')
async def back(message:types.Message):
    await start(message)
    
class OrderState(StatesGroup):
    full_name = State()
    product = State()
    number = State()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        product TEXT,
        number TEXT)''')
    cursor.connection.commit()

@dp.message_handler(text='Оформить заказ')
async def order(message:types.Message):
    await message.answer("Ваше полное имя:")
    await OrderState.full_name.set()
    
@dp.message_handler(state=OrderState.full_name)
async def name(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text
    
    await message.answer("Товар который хотите заказать:")
    await OrderState.product.set()
    
@dp.message_handler(state=OrderState.product)
async def product(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['product'] = message.text
        
    await message.answer("Ваш номер телефона:")
    await OrderState.number.set()
    
@dp.message_handler(state=OrderState.number)
async def number(message:types.Message, state:FSMContext):
    try:
        async with state.proxy() as data:
            data['number'] = int(message.text)
        await state.finish()
        await message.answer("Заказ принят!")       
    except ValueError:
        await message.answer("Вводите цифры а не буквы!")
    except Exception as e:
        logging.error(f"Error in number handler: {e}")
        
    cursor.execute("INSERT INTO orders (full_name, product, number) VALUES (?,?,?)",
                   data['full_name'], data['product'], data['number']) 
    cursor.connection.commit()

@dp.message_handler(text='Часто задаваемые вопросы')
async def question(message:types.Message):
    await message.answer('''Какой операционной системой оснащен этот ноутбук?
 • Наш ноутбук поставляется с предустановленной операционной системой Windows 10/11 или macOS, в зависимости от модели.
  Какова продолжительность работы от аккумулятора?
 • Время работы от аккумулятора может варьироваться в зависимости от модели и интенсивности использования, но в среднем наши ноутбуки обеспечивают от 6 до 12 часов автономной работы.
  Какова гарантийная политика на этот ноутбук?
 • Мы предоставляем стандартную гарантию производителя на наши ноутбуки, которая обычно составляет 1 год. Дополнительные опции гарантии также могут быть доступны.
  Можно ли расширить объем оперативной памяти?
 • Для большинства наших ноутбуков есть возможность расширения оперативной памяти. Однако это может зависеть от конкретной модели. Рекомендуется обратиться к сервисному центру или ознакомиться с документацией к ноутбуку.
  Какова скорость процессора и объем жесткого диска?
 • Характеристики процессора и объем жесткого диска могут различаться в зависимости от модели. Мы рекомендуем ознакомиться с подробными спецификациями нашего ноутбука для получения точной информации.
  Поддерживает ли этот ноутбук беспроводные соединения?
 • Да, наши ноутбуки обычно поддерживают беспроводные соединения, такие как Wi-Fi и Bluetooth, для беспроводного доступа в интернет и подключения других устройств.
  Есть ли у него разъемы USB-C или Thunderbolt?
 • Некоторые наши ноутбуки оснащены разъемами USB-C или Thunderbolt, однако это может зависеть от модели. Мы рекомендуем ознакомиться с подробными спецификациями конкретного ноутбука.
  Можно ли обновить графический процессор?
 • В большинстве случаев графический процессор наших ноутбуков не подлежит обновлению, так как он интегрирован в материнскую плату или процессор. Однако мы можем предложить выбор из различных моделей с разными видеокартами.
Это лишь несколько примеров часто задаваемых вопросов о ноутбуках в магазинах, и ответы могут варьироваться в зависимости от конкретной модели и бренда.
Если у вас остались еще вопросы то пишите админу @dvuuud''')
    
@dp.message_handler(text='Назад')
async def back(message:types.Message):
    await start(message)
    
@dp.message_handler()
async def not_found(message:types.Message):
    await message.answer("Я вас не понимаю!")
    
executor.start_polling(dp, skip_updates=True)