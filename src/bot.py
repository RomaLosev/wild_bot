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
VALUE_ERROR = (
    'Неправильный запрос.\n'
    'Ожидается <артикул> <запрос>\n'
    'Например: 37260674 Омега 3 (для одиночного поиска)\n'
    '74788280/74778293 велосипед (для поиска нескольких артикулов)'
)

logger.add("logger_bot.log", enqueue=True)


@dp.message_handler(commands=['start'])
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    logger.info(f'User {message.from_user.full_name}, started bot ')
    await message.answer(f' Привет, {message.from_user.full_name}!\n'
                         'Посмотрим где там твой товар?)\n'
                         'Запрос в формате <артикул> <запрос>\n'
                         'Например: 37260674 Омега 3 (для одиночного поиска)\n'
                         '74788280/74778293 велосипед (для поиска нескольких артикулов)')


@dp.message_handler(content_types=['text'])
async def answer_handler(message: Message) -> None:
    """
    Handler get {item_id search_query}for single search
    OR {item_id/item_id/... search_query} for multy search
    """
    logger.info(f'User {message.from_user.full_name}, search {message.text}')
    logger.info(message.text)
    try:
        result = finder.main(message.text)
        await message.answer(text=result)
    except ValueError as error:
        logger.error(error)
        await message.answer(text=VALUE_ERROR)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
