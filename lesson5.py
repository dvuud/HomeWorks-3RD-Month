from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging, sqlite3, time

bot = Bot(token='6772813670:AAGnS78l6CvMujKSjzPs2XFgM0yJwEy9Ea0')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

connection = sqlite3.connect('itbot.db')
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id VARCHAR(255),
    first_name VARCHAR(255),        
    last_name VARCHAR(255),        
    username VARCHAR(255),        
    created VARCHAR(255)      
);
""")
cursor.execute('''CREATE TABLE IF NOT EXISTS application(
               id INTEGER PRIMARY KEY,
               first_name VARCHAR(255),
               last_name VARCHAR(255),
               phone INTEGER,
               direction VARCHAR(255),
               note VARCHAR(255),
               data_joined VARCHAR(255)
)''')
cursor.connection.commit()
start_buttons = [
    types.KeyboardButton('О нас'),
    types.KeyboardButton('Адрес'),
    types.KeyboardButton('Курсы'),
    types.KeyboardButton('Отправить заявку')
]
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_buttons)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    cursor.execute(f"SELECT id FROM users WHERE id = {message.from_user.id};")
    result = cursor.fetchall()
    print(result)
    if result == []:
        cursor.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                       (message.from_user.id, message.from_user.first_name,
                        message.from_user.last_name, message.from_user.username, time.ctime()))
        cursor.connection.commit()
    await message.answer(f"Здраствуйте {message.from_user.full_name}", reply_markup=start_keyboard)

@dp.message_handler(text="О нас")
async def about_us(message:types.Message):
    await message.reply("Geeks - это айти курсы в Бишкеке, Оше, Кара-Балте и в Ташкенте")

@dp.message_handler(text='Адрес')
async def send_address(message:types.Message):
    await message.answer("Наш адрес: Мырзалы Аматова 1Б")
    await message.answer_location(40.5193216724554, 72.8030109959693)

courses_buttons = [
    types.KeyboardButton('Backend'),
    types.KeyboardButton('Frontend'),
    types.KeyboardButton('UX/UI'),
    types.KeyboardButton('Android'),
    types.KeyboardButton('iOS'),
    types.KeyboardButton('Назад')
]
courses_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*courses_buttons)

@dp.message_handler(text='Курсы')
async def send_couses(message:types.Message):
    await message.answer("Вот наши курсы:", reply_markup=courses_keyboard)

@dp.message_handler(text='Backend')
async def backend(message:types.Message):
    await message.reply("Backend - это внутреняя часть сайта которая не видна вам")

@dp.message_handler(text="Frontend")
async def frontend(message:types.Message):
    await message.reply("Frontend - это лицевая сторона сайта которая видна вам")

@dp.message_handler(text="UX/UI")
async def uxui(message:types.Message):
    await message.reply("UX/UI - это дизайн сайта или приложения")

@dp.message_handler(text="Android")
async def android(message:types.Message):
    await message.reply("Android - это приложение на операционную систему Android")

@dp.message_handler(text="iOS")
async def ios(message:types.Message):
    await message.reply("iOS - это операционная система на Apple")

@dp.message_handler(text='Назад')
async def rollback(message:types.Message):
    await start(message)

class ApplicationState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    direction = State()
    note = State()

@dp.message_handler(text="Отправить заявку")
async def get_lids(message:types.Message):
    await message.answer("Для оставления заявку на курс вам необходимо ввести следующие данные:")
    await message.answer("Имя, Фамиля, Номер, Направление, Примечание (если есть)")
    await message.answer("Введите имя:")
    await ApplicationState.first_name.set()

@dp.message_handler(state=ApplicationState.first_name)
async def get_last_name(message:types.Message, state:FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введите фамилию:")
    await ApplicationState.last_name.set()

@dp.message_handler(state=ApplicationState.last_name)
async def get_phone(message:types.Message, state:FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введите номер")
    await ApplicationState.phone.set()

@dp.message_handler(state=ApplicationState.phone)
async def get_direction(message:types.Message, state:FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите направление", reply_markup=courses_keyboard)
    await ApplicationState.direction.set()

@dp.message_handler(state=ApplicationState.direction)
async def get_note(message:types.Message, state:FSMContext):
    await state.update_data(direction=message.text)
    await message.answer("Примерчание (если есть)")
    await ApplicationState.note.set()

@dp.message_handler(state=ApplicationState.note)
async def send_application(message:types.Message, state:FSMContext):
    await state.update_data(note=message.text)
    await message.answer("Все данные записаны")
    result = await storage.get_data(user=message.from_user.id)
    send_message = f"""Заявка на курсы {time.ctime()}
Имя: {result['first_name']}
Фамилия: {result['last_name']}
Номер: {result['phone']}
Направление: {result['direction']}
Примечание: {result['note']}
Дата: {time.ctime()}"""
    await message.answer(f"{result}")
    await bot.send_message(-4142647964, f"{send_message}")
    
    cursor.execute('''INSERT INTO application (first_name, last_name, phone, direction, note, data_joined) VALUES (?,?,?,?,?,?)''',
                   (result['first_name'], result['last_name'], result['phone'], result['direction'], result['note'], time.ctime()))
    cursor.connection.commit()

@dp.message_handler()
async def not_found(message:types.Message):
    await message.reply("Я вас не понял, введите /start")

executor.start_polling(dp)