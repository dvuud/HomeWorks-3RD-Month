from aiogram import Bot, Dispatcher, types, executor
import logging 
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import state, StatesGroup
# import requests, os
from config import token

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot,storage=storage)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer(f"Привет {message.from_user.full_name}, отправь ТикТок ссылку! ")
    
@dp.message_handler()
async def get_url(message:types.Message):
        await message.reply("Начинаю скачивать видео...")
        get_id_video = message.text.split('?')
        current_id = get_id_video[0].split('/')[5]
        video_api = requests.get(f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={current_id}').json()
        video_url = video_api.get('aweme_list')[0].get('video').get('play_addr').get('url_list')[0]
        if video_url:
            title_video = video_api.get('aweme_list')[0].get('desc')
        print("скачиваем видео...")
        try:
            with open(f'video/{title_video}.mp4','wb') as video_file:
                video_file.write(requests.get(video_url).content)
            print('Видео успешно скачан в шапку video')
        except Exception as error:
            print(f'Error: {error}')
        try:
            with open(f'video/{title_video}.mp4', 'rb') as send_file:
                await message.answer_video(send_file)
                await message.answer("Ваше видео готово!")
        except Exception as error:
            await message.answer(f"Ошибка: {error}")
            await message.answer("Ошибка, повторите заново")
     

executor.start_polling(dp)
 