import os
import time

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
                         'Посмотрим где там твой товар?)')


@dp.message_handler(content_types=['text'])
async def answer_handler(message: Message) -> None:
    """
    Handler get {item_id} and {search_query}
    """
    logger.info(f'User {message.from_user.full_name}, search {message.text}')
    try:
        start = time.time()
        id, query = message.text.split(maxsplit=1)
        result = finder.main(int(id), query)
        execution_time = time.time()-start
        if result:
            logger.info(result)
            await message.answer(text=result)
            await message.answer(text='Найдено за {:.02f}сек.'.format(execution_time))
        else:
            await message.answer(text='Не найдено')
    except ValueError as error:
        await message.answer(f'Неправильный запрос {error}')


def main() -> None:
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
