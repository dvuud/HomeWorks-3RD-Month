# Импортируем все нужные нам модули
import logging
import sqlite3
import time
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = Bot(token='6773327371:AAGgtBJA-vOaZFJQd30nweZhcuFVq2l2UHY')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

# Создаем  базу данных 

with sqlite3.connect('Bank.db') as connection:
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        full_name VARCHAR(255), 
        id_passport INTEGER,                   
        age INTEGER,
        id_balance TEXT,
        balance INTEGER DEFAULT 0, 
        data_joined DATETIME      
    );
    """)
    cursor.connection.commit()

# Создаем класс State что-бы включить в работу Машиносостояний

class StateUser(StatesGroup):
    full_name = State()
    id_passport = State()
    age = State()
    id_balance = State()
    summa = State()
    transfer_id = State()
    transfer_summa = State()

@dp.message_handler(commands='start')
async def start(message: types.Message):
    try:
        user_id = message.from_user.id
        
        cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
        user = cursor.fetchone()
        
        if user is not None:
            await message.answer(
                """Добро пожаловать в банк!
                Для пополнения и просмотра текущего баланса введите: /balance,
                Для вывода средств: /transfer"""
            )
        else:
            await message.answer(
                """Добро пожаловать в банк!
                Для пополнения и просмотра текущего баланса нажмите: /balance,
                Для вывода средств: /transfer
                Но перед этим давайте зарегистрируемся!"""
            )
            await message.answer("Введите полное имя?")
            await StateUser.full_name.set()
    except Exception as e:
        logging.error(f"Error in start handler: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз или отмените операцию.")

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
            data['id_passport'] = int(message.text)

        await StateUser.age.set()
        await message.answer("Отлично, ваш возраст?")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный номер паспорта.")
    except Exception as e:
        logging.error(f"Error in passport handler: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз или отмените операцию.")

@dp.message_handler(state=StateUser.age)
async def age(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['age'] = int(message.text)
            
# Сохраняем все в базу данных

        cursor.execute(
            '''INSERT INTO users (id, full_name, id_passport, age, data_joined) 
            VALUES (?,?,?,?,?)''',
            (message.from_user.id, data['full_name'], data['id_passport'], data['age'], time.time())
        )
        connection.commit()
        await state.finish()
        await message.answer("Регистрация прошла успешно!")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст.")
    except Exception as e:
        logging.error(f"Error in age handler: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз или отмените операцию.")

# Создаем InlineKeyboard для команды "Пополнить баланс"

in_keyboard = [
    types.KeyboardButton("Пополнить баланс")
]
start_in_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*in_keyboard)

@dp.message_handler(commands='balance')
async def balance(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = cursor.fetchone()

    if user is not None:
        user_balance = user[5]
        await message.reply(f"""ID баланса: {message.from_user.id}
Ваш текущий баланс: {user_balance}""", reply_markup=start_in_buttons)
    else:
        await message.reply("Вы не зарегистрированы. Используйте /start для регистрации.")

@dp.message_handler(text='Пополнить баланс')
async def abc(message: types.Message):
    await message.answer("Введите ID вашего баланса: ")
    await StateUser.id_balance.set()

@dp.message_handler(state=StateUser.id_balance)
async def acd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id_balance'] = int(message.text)

    await StateUser.summa.set()
    await message.answer("Теперь введите сумму перевода:")

@dp.message_handler(state=StateUser.summa)
async def ags(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['summa'] = int(message.text)
        
# Опять таки сохраняем в базу данных
        
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id_balance = ?", (data['summa'], data['id_balance']))
        cursor.connection.commit()

    await state.finish()
    await message.answer("Пополнение успешно!")

@dp.message_handler(commands='transfer')
async def transfer(message: types.Message):
    await message.answer("Введите ID получателя:")
    await StateUser.transfer_id.set()
    
@dp.message_handler(state=StateUser.transfer_id)
async def id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
            data['transfer_id'] = int(message.text)
    
    await StateUser.transfer_summa.set()
    await message.answer("Введите сумму перевода:")

@dp.message_handler(state=StateUser.transfer_summa)
async def summma(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['transfer_summa'] = int(message.text)
            user_id = message.from_user.id
            cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
            user = cursor.fetchone()
            user_balance = user[5]
                
            cursor.execute("UPDATE users SET balance = balance - ? WHERE id_balance = ?", (data['transfer_summa'], data['id_balance']))
            cursor.connection.commit()

            await state.finish()

            if user_balance >= data['transfer_summa']:
                await message.answer("Перевод выполнен!")
            else:
                await message.answer("Недостаточно средств, чтобы перевести!")

executor.start_polling(dp, skip_updates=True)
