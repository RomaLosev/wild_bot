import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from dotenv import load_dotenv
from loguru import logger

from finder import Finder

load_dotenv()


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
finder = Finder()

logger.add("logger_bot.log", enqueue=True)


@dp.message_handler(commands=['start'])
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    logger.info(f'User {message.from_user.full_name}, started bot ')
    await message.answer(f' Привет, {message.from_user.full_name}!\n'
                         'Посмотрим где там твой товар?)\n'
                         'Запрос в формате "Артикул поисковый запроc"')


@dp.message_handler(content_types=['text'])
async def answer_handler(message: Message) -> None:
    """
    Handler get {item_id} and {search_query}
    """
    logger.info(f'User {message.from_user.full_name}, search {message.text}')
    logger.info(message.text)
    try:
        result = finder.main(message.text)
        await message.answer(text=result)
    except ValueError as error:
        logger.error(f'Error: {error}')
        await message.answer(text='Неправильный запрос')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
