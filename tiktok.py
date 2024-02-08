import requests, os

input_url = input("URL: ")
print(input_url)

current_id = input_url.split('/')[5].split('?')[0]
print(current_id)
video_api = requests.get(f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={current_id}').json()
print(video_api)
video_url = video_api.get('aweme_list')[0].get('video').get('play_addr').get('url_list')[0]
print(video_url)
if video_url:
    print("Начинаю скачивать видео...")
    try:
        os.mkdir('video')
    except:
        print("Папка video создана")
        
    try:
        with open(f'video/{current_id}.mp4', 'wb') as vd_file:
            vd_file.write(requests.get(video_url).content)
        print("Видео успешно скачано")
    except:
        print("Произошла ошибка при скачивании видео")
        