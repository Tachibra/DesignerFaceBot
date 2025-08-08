import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from PIL import Image

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

OVERLAY_PATH = "overlay.png"

print("🚀 Бот запускается...")

app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.photo & filters.mentioned)
async def handle_image(client, message):
    try:
        print("📥 Получено новое сообщение с фото и упоминанием бота")

        # Скачиваем фото
        photo_path = await message.download()
        print(f"📁 Фото загружено: {photo_path}")

        # Открываем основное изображение
        with Image.open(photo_path).convert("RGBA") as base_img:
            width, height = base_img.size
            print(f"🖼 Размер базового изображения: {width}x{height}")

            # Проверка на наличие PNG
            if not os.path.exists(OVERLAY_PATH):
                print("❌ Файл overlay.png не найден!")
                await message.reply("Файл overlay.png отсутствует на сервере.")
                return

            print("🔧 Открываем overlay.png")
            with Image.open(OVERLAY_PATH).convert("RGBA") as overlay:
                scale_factor = width // 3
                overlay_ratio = overlay.height / overlay.width
                new_overlay = overlay.resize((scale_factor, int(scale_factor * overlay_ratio)))

                pos_x = 0
                pos_y = height - new_overlay.height

                print(f"📌 Накладываем overlay в точку: ({pos_x}, {pos_y})")
                base_img.alpha_composite(new_overlay, (pos_x, pos_y))

                output_path = f"output_{message.id}.png"
                base_img.save(output_path)
                print(f"💾 Сохранено: {output_path}")

        # Отправляем пользователю
        await message.reply_photo(output_path)
        print("✅ Ответ отправлен пользователю")

        # Чистим временные файлы
        os.remove(output_path)
        os.remove(photo_path)
        print("🧹 Временные файлы удалены")

    except Exception as e:
        print(f"❌ Ошибка при обработке изображения: {e}")
        await message.reply("Произошла ошибка при обработке изображения 😢")

app.run()
