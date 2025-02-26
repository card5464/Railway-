import logging
import requests
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.utils.markdown import hbold
from fastapi import FastAPI
import uvicorn

# Railway automatic port ke liye
PORT = int(os.getenv("PORT", 5000))  # Railway recommended port 5000

# Telegram Bot Token
API_TOKEN = os.getenv("API_TOKEN")  # Railway pe API_TOKEN as environment variable set karein

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Enable logging
logging.basicConfig(level=logging.INFO)

# FastAPI Web Server
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Bot is running on Railway.app 24/7!"}

# BIN Lookup Function
def get_bin_info(bin_number):
    url = f"https://lookup.binlist.net/{bin_number}"
    headers = {"Accept-Version": "3"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return f"BIN: {bin_number}\n" \
                   f"Brand: {data.get('scheme', 'Unknown')}\n" \
                   f"Type: {data.get('type', 'Unknown')}\n" \
                   f"Bank: {data.get('bank', {}).get('name', 'Unknown')}\n" \
                   f"Country: {data.get('country', {}).get('name', 'Unknown')}"
        else:
            return "Invalid BIN or API limit reached."
    except:
        return "Error fetching BIN data."

# Telegram Command Handlers
@dp.message(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"Hello! Send me a {hbold('BIN (first 6 digits of a card)')} to check.")

@dp.message()
async def bin_lookup(message: types.Message):
    bin_number = message.text.strip()
    if bin_number.isdigit() and len(bin_number) == 6:
        result = get_bin_info(bin_number)
        await message.answer(result)
    else:
        await message.answer("Please enter a valid 6-digit BIN.")

# Function to Start Web Server
async def run_web():
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT)
    server = uvicorn.Server(config)
    await server.serve()

# Function to Start Bot
async def start_bot():
    await bot.set_my_commands([BotCommand(command="start", description="Start the bot")])
    await dp.start_polling(bot)

async def main():
    await asyncio.gather(run_web(), start_bot())  # Run bot and FastAPI server together

if __name__ == '__main__':
    asyncio.run(main())
