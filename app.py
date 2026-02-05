import telebot
from PIL.ImageFile import ImageFile
from PIL.ImageMath import lambda_eval
from telebot import types
from PIL import Image, ImageFilter , ImageEnhance , ImageDraw
import os
import uuid

TOKEN = os.getenv("8495336542:AAEizshCNjKWehppbjMqf_cWmcdihiFtam4")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не заданий у змінних середовища")

bot = telebot.TeleBot(TOKEN)

PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

user_photos = {}


def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Блюр", "Сильеий блюр")
    kb.add("Чорно-білий","Сепія")
    kb.add("Контраст", "Яскравість")
    kb.add("Різкість", "Дзеркало")
    kb.add("Скинути")
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
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)

        path = os.path.join(PHOTO_DIR, f"{message.chat.id}.jpg")
        with open(path, "wb") as f:
            f.write(downloaded)

        user_photos[message.chat.id] = path
        bot.send_message(message.chat.id, "Фото отримано.  Обирай філтьр")
    except:
        bot.send_message(message.chat.id , "Помилка при завантаженні фото")


@bot.message_handler(func=lambda m: m.text in [
    "Блюр", "Сильний блюр" , "Чорно-білий" , "Сепія",
    "Контраст", "Яскравість", "Різкість", "Дзеркало"
])
def filters(message):
    apply_filter(message, message.text)

@bot.message_handler(func=lambda m: m.text == "Скинути")
def reset(message):
    path = user_photos.pop(message.chat.id, None)
    if path and os.path.exists(path):
        os.remove(path)
    bot.send_message(message.chat.id, "Фото скинуто. Наділши нове")

def apply_filter(message, mode):
    chat_id = message.chat.id

    if chat_id not in user_photos:
        bot.send_message(chat_id, "Спочатку надішли фото")
        return

    try:
        img = Image.open(user_photos[chat_id]).convert("RGB")

        if mode == "Блюр":
            img = img.filter(ImageFilter.BLUR)

        elif mode == "Сильний блюр":
            img = img.filter(ImageFilter.GaussianBlur(5))

        elif mode == "Чорний-білий":
            img = img.convert("L")

        elif mode == "Контраст":
            img = ImageEnhance.Contrast(img).enhance(2)

        elif mode == "Яскравість":
            img = ImageEnhance.Brightness(img).enhance(1.5)

        elif mode == "Дзеркало":
            img = img.transform(Image.FLIP_LEFT_RIGHT)

        elif mode == "Сепія":
            gray = img.convert("L")
            img = Image.merge(
                "RGB",
                (
                    gray.point(lambda x: x * 1.1),
                    gray.point(lambda x: x * 0.9),
                    gray.point(lambda x: x * 0.7),
                )
            )

        out_path = os.path.join(PHOTO_DIR, f"{chat_id}_out.jpg")
        img.save(out_path)

        with open(out_path, "rb") as f:
            bot.send_photo(chat_id, f)

        os.remove(out_path)
    except Exception as e:
        bot.send_message(chat_id, "Помилка обробки фото")


print("📸 Photo bot запущений...")
bot.infinity_polling()
