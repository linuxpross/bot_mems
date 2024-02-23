import telebot
from telebot import types
from Token import TOKEN
import cv2
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import requests
import numpy as np
import random

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id, 'привет ето бот неиросет киин фото и он наидот в ном человека')

@bot.message_handler(commands=['help'])
def send_message_help(message):
    bot.send_message(message.chat.id, 'привет по всем вапросвм к автору бота ')

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Проверяем, есть ли у пользователя активная сессия для отправки текста на изображение
    if message.chat.id in TEXT_TO_IMAGE_SESSION:
        text_to_image(message)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте сначала фотографию, на которую нужно нанести текст.')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.send_message(message.chat.id, 'Теперь отправьте текст, который нужно написать на фотографии.')
        # Добавляем в сессию id пользователя для отправки текста на изображение
        TEXT_TO_IMAGE_SESSION.add(message.chat.id)
        # Получаем информацию о фото
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        # Сохраняем ссылку на фото для последующего использования
        USER_PHOTO_URL[message.chat.id] = file_url
        
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

def text_to_image(message):
    try:
        text = message.text
        user_id = message.chat.id
        file_url = USER_PHOTO_URL.get(user_id)
        
        # Читаем изображение с помощью OpenCV
        response = requests.get(file_url)
        img_bytes = BytesIO(response.content)
        img = Image.open(img_bytes)
        
        # Создаем объект ImageDraw для отображения текста на изображении
        draw = ImageDraw.Draw(img)
        # Указываем путь к файлу шрифта
        font_path = "ofont.ru_Angry Birds.ttf"  # Путь к вашему TTF файлу
        # Загружаем шрифт
        font = ImageFont.truetype(font_path, 36)  # 36 - размер шрифта

        draw.text((10, 10), text, fill=(255,0,12), font=font)  # Отображаем текст на изображении

        # Сохраняем и отправляем обработанное изображение
        image_path = 'temp_image.jpg'
        img.save(image_path, 'JPEG')
        with open(image_path, 'rb') as photo:
            bot.send_photo(user_id, photo)
        
        # Удаляем данные о пользователе из сессии
        TEXT_TO_IMAGE_SESSION.remove(user_id)
        del USER_PHOTO_URL[user_id]
        
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Сессия для хранения данных о пользователях, ожидающих отправку текста на изображение
TEXT_TO_IMAGE_SESSION = set()
# Словарь для хранения ссылок на фотографии, которые отправил пользователь (ключ - id пользователя)
USER_PHOTO_URL = {}

# Обработчик видео
bot.polling()
