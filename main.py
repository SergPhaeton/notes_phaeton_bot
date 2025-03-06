import asyncio
import logging
import re
from datetime import datetime
import dateparser
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.utils import executor

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()
scheduler.start()

def parse_message(text):
    match = re.search(r'напомни мне (.+)', text, re.IGNORECASE)
    if match:
        full_text = match.group(1)
        parts = full_text.rsplit(" сделать ", 1)
        if len(parts) == 2:
            time_part, task = parts
        else:
            time_part, task = full_text, "что-то важное"
        
        reminder_time = dateparser.parse(time_part, languages=['ru'])
        if reminder_time:
            if reminder_time < datetime.now():
                return None, None  # Прошедшее время не подойдёт
            return reminder_time, task
    return None, None

@dp.message_handler(lambda message: "напомни мне" in message.text.lower())
async def set_reminder(message: Message):
    reminder_time, task = parse_message(message.text)
    if reminder_time:
        scheduler.add_job(send_reminder, "date", run_date=reminder_time, args=[message.chat.id, task])
        await message.reply(f"Окей, напомню тебе {reminder_time.strftime('%d.%m %H:%M')} сделать '{task}'.")
    else:
        await message.reply("Я не смог понять время напоминания. Попробуй, например: 'напомни мне завтра в 7 утра сделать зарядку' или 'напомни мне через 30 минут позвонить'.")

async def send_reminder(chat_id, task):
    await bot.send_message(chat_id, f"🔔 Напоминание: {task}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
