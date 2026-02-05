import telebot
from PIL.ImageFile import ImageFile
from PIL.ImageMath import lambda_eval
from telebot import types
from PIL import Image, ImageFilter , ImageEnhance
import os
import uuid

TOKEN = "8495336542:AAEizshCNjKWehppbjMqf_cWmcdihiFtam4"
bot = telebot.TeleBot(TOKEN, parse_mode=None)

PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

user_photos = {}


def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Блюр", "Чорно-білий")
    kb.add("Контраст")
    return kb


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "📸 Надішли фото та обери фільтр ",
        reply_markup=main_keyboard()
    )

#отриманння фот
@bot.message_handler(content_types=['photo'])
def get_photo(message):
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)

        path = f"{message.chat.id}.jpg"
        with open(path, "wb") as f:
            f.write(downloaded)

        user_photos[message.chat.id] = path
        bot.send_message(message.chat.id, "Фото отримано.  Обирай філтьр")

#blur
@bot.message_handler(func=lambda m: m.text == "Блюр")
def blur_photo(message):
    apply_filter(message, "blur")

#чорний-білий
@bot.message_handler(func=lambda m: m.text == "Чорно-білий")
def bw_photo(message):
    apply_filter(message , "bw")

#контраст
@bot.message_handler(func=lambda m: m.text == "Контраст")
def contrast_photo(message):
    apply_filter(message, "contrast")

def apply_filter(message, mode):
    chat_id = message.chat.id

    if chat_id not in user_photos:
        bot.send_message(chat_id, "Спочатку надішли фото")
        return

    img = Image.open(user_photos[chat_id]).convert("RGB")

    if mode == "blur":
        img = img.filter(ImageFilter.BLUR)

    elif mode == "bw":
        img = img.convert("L")

    elif mode == "contrast":
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

    out = f"{chat_id}_out.jpg"
    img.save(out)

    with open(out, "rb") as f:
        bot.send_photo(chat_id, f)

    os.remove(out)


print("📸 Photo bot запущений...")
bot.infinity_polling()
