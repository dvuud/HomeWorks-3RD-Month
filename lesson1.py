from aiogram import Bot, Dispatcher, types, executor

bot = Bot(token='6820991809:AAGmxA1OXFwCwmOjS13Myi_0bLKvkPcXvNg')
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer("Привет мир! И привет Geeks Python")

@dp.message_handler(commands='help')
async def help(message:types.Message):
    await message.answer("Чем могу вам помочь?")

@dp.message_handler(text="Geeks")
async def geeks(message:types.Message):
    await message.answer("Geeks - айти курсы в Бишкеке и Оше")

@dp.message_handler(commands='test')
async def test(message:types.Message):
    print(message)
    await message.answer(f"Здраствуйте {message.from_user.full_name}")
    await message.answer(f"Ваш username @{message.from_user.username}")
    await message.reply("reply - это выделение текста и ответ к нему")
    await message.answer_location(40.5193216724554, 72.8030109959693)
    # await message.answer_photo('https://geeks.kg/back_media/main_block/2023/06/22/96425634-e4e2-44ae-8f86-243519f735f3.webp')
    # await message.answer_contact('+996772343206', "Toktorov", "Kurmanbek")
    # await message.answer_dice(emoji='🎰')
    with open('voice.m4a', 'rb') as my_voice:
        await message.answer_voice(my_voice)
    with open('voice.m4a', 'rb') as my_voice:
        await message.answer_audio(my_voice)

@dp.message_handler()
async def not_found(message:types.Message):
    await message.reply("Я вас не понял, введите /help")

executor.start_polling(dp)