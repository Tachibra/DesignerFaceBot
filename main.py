import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from PIL import Image

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

OVERLAY_PATH = "overlay.png"

app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.photo & filters.mentioned)
async def handle_image(client, message):
    photo = await message.download()

    with Image.open(photo).convert("RGBA") as base_img:
        width, height = base_img.size

        with Image.open(OVERLAY_PATH).convert("RGBA") as overlay:
            scale_factor = width // 3
            overlay_ratio = overlay.height / overlay.width
            new_overlay = overlay.resize((scale_factor, int(scale_factor * overlay_ratio)))

            pos_x = 0
            pos_y = height - new_overlay.height

            base_img.alpha_composite(new_overlay, (pos_x, pos_y))

            output_path = f"output_{message.id}.png"
            base_img.save(output_path)

            await message.reply_photo(output_path)
            os.remove(output_path)
            os.remove(photo)

app.run()
