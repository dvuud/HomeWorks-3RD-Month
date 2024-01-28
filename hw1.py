from aiogram import Bot, Dispatcher, types, executor
import random

bot = Bot(token='6769258083:AAHSbniG2od4nnJ4dJLdisnNIhp6jPlJzaE')
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer(f"Привет {message.from_user.first_name} давай поиграем в игру,я загадал число от 1 до 3, угадай число!!!")

@dp.message_handler()
async def gues_num(message:types.Message):
        try:
            user_num = int(message.text)
        
        except ValueError:
            await message.reply("Я вас не понимаю, введите число!")

        random_num = random.randint(1,3)
        if user_num == random_num and user_num < 4:
            await message.reply("Правильно вы отгадали!")
            await message.answer_photo('https://media.makeameme.org/created/you-win-nothing-b744e1771f.jpg')
        else:
            await message.reply("Неправильно, повторите заново!")
            await message.answer_photo('https://media.makeameme.org/created/sorry-you-lose.jpg')
        
        while True:
            if user_num > 3:
                await message.reply("Я загадал число от 1 до 3, не больше!!!")
                break
            else:
                continue

executor.start_polling(dp)