import os
import random
from pyrogram import Client, filters
from PIL import Image
import logging

# --------------------
# Логирование
# --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --------------------
# Конфиг
# --------------------
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OVERLAY_PATH = "overlay.png"
OVERLAY2_PATH = "overlay2.png"

app = Client("overlay_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# --------------------
# Функция наложения overlay.png (нижний левый угол, треть ширины)
# --------------------
def overlay_image(base_path, output_path):
    with Image.open(base_path).convert("RGBA") as base_img:
        width, height = base_img.size
        logging.info(f"Размер исходного изображения: {width}x{height}")

        if not os.path.exists(OVERLAY_PATH):
            raise FileNotFoundError("overlay.png отсутствует на сервере!")

        with Image.open(OVERLAY_PATH).convert("RGBA") as overlay:
            scale_factor = width // 3
            overlay_ratio = overlay.height / overlay.width
            new_overlay = overlay.resize((scale_factor, int(scale_factor * overlay_ratio)))

            pos_x = 0
            pos_y = height - new_overlay.height
            base_img.alpha_composite(new_overlay, (pos_x, pos_y))
            base_img.save(output_path)


# --------------------
# Функция наложения overlay2.png (случайный размер, место, поворот)
# --------------------
def overlay_image_random(base_path, output_path):
    with Image.open(base_path).convert("RGBA") as base_img:
        width, height = base_img.size
        logging.info(f"Размер исходного изображения: {width}x{height}")

        if not os.path.exists(OVERLAY2_PATH):
            raise FileNotFoundError("overlay2.png отсутствует на сервере!")

        with Image.open(OVERLAY2_PATH).convert("RGBA") as overlay:
            # Случайный размер — от 10% до 50% ширины
            scale_factor = random.randint(width // 10, width // 2)
            overlay_ratio = overlay.height / overlay.width
            overlay_resized = overlay.resize((scale_factor, int(scale_factor * overlay_ratio)))

            # Случайный угол поворота
            angle = random.randint(0, 359)
            overlay_rotated = overlay_resized.rotate(angle, expand=True)

            # Случайное место
            pos_x = random.randint(0, max(0, width - overlay_rotated.width))
            pos_y = random.randint(0, max(0, height - overlay_rotated.height))

            base_img.alpha_composite(overlay_rotated, (pos_x, pos_y))
            base_img.save(output_path)


# --------------------
# Обработка фото с упоминанием бота
# --------------------
@app.on_message(filters.photo & filters.mentioned)
async def handle_photo_mention(client, message):
    try:
        logging.info("Получено фото с упоминанием бота")
        photo_path = await message.download()
        output_path = f"output_{message.id}.png"

        overlay_image(photo_path, output_path)

        await message.reply_photo(output_path)
        logging.info("Фото отправлено в ответ (упоминание)")

        os.remove(photo_path)
        os.remove(output_path)
    except Exception as e:
        logging.error(f"Ошибка при обработке упоминания: {e}")
        await message.reply("Произошла ошибка при обработке фото.")


# --------------------
# Команда /df — нижний левый угол overlay.png
# --------------------
@app.on_message(filters.command(["df"], prefixes="/"))
async def handle_reply_df(client, message):
    try:
        logging.info("Получена команда /df")

        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply("❌ Нужно ответить этой командой на сообщение с фото.")
            return

        photo_path = await message.reply_to_message.download()
        output_path = f"output_{message.id}.png"

        overlay_image(photo_path, output_path)

        await message.reply_photo(output_path)
        logging.info("Фото отправлено в ответ (/df)")

        os.remove(photo_path)
        os.remove(output_path)
    except Exception as e:
        logging.error(f"Ошибка в /df: {e}")
        await message.reply("Произошла ошибка при обработке фото.")


# --------------------
# Команда /ms — случайный размер, место, поворот overlay2.png
# --------------------
@app.on_message(filters.command(["ms"], prefixes="/"))
async def handle_reply_ms(client, message):
    try:
        logging.info("Получена команда /ms")

        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply("❌ Нужно ответить этой командой на сообщение с фото.")
            return

        photo_path = await message.reply_to_message.download()
        output_path = f"output_{message.id}.png"

        overlay_image_random(photo_path, output_path)

        await message.reply_photo(output_path)
        logging.info("Фото отправлено в ответ (/ms)")

        os.remove(photo_path)
        os.remove(output_path)
    except Exception as e:
        logging.error(f"Ошибка в /ms: {e}")
        await message.reply("Произошла ошибка при обработке фото.")


# --------------------
# Запуск бота
# --------------------
if __name__ == "__main__":
    logging.info("Бот запущен...")
    app.run()
