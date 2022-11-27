import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union

import requests
from loguru import logger

JSON = Union[dict[str, any]]

STORES = '116433,115577,117501,507,3158,2737,1699'
# возможно, эта переменная отвечает за пункты выдачи,
# но мне не удалось поймать разницу в выдаче за счёт её изменения

logger.add("logger_finder.log", enqueue=True)


class Finder:

    @staticmethod
    def get_urls(query: str) -> dict:
        """
        dict{page: url} need page to know which page we parse
        :param query: str: search_query
        :return: dict{page: data}
        """
        urls = {}
        for page in range(1, 101):
            urls[page] = (
                f'https://search.wb.ru/'
                f'exactmatch/ru/common/v4/search?appType=1&'
                f'couponsGeo=12,3,18,15,21&'
                f'curr=rub&'
                f'dest=-1029256,-102269,-2162196,-1255942&'
                f'emp=0&'
                f'lang=ru&'
                f'locale=ru&'
                f'pricemarginCoeff=1.0&'
                f'stores={STORES}&'
                f'query={query}&'
                f"page={page}&"
                f'reg=0&'
                f'regions='
                f'80,64,83,4,38,33,70,82,69,68,86,75,30,40,48,1,22,66,31,71&'
                f'resultset=catalog&'
                f'sort=popular&'
                f'spp=0&'
                f'suppressSpellcheck=false'
            )
        return urls

    @staticmethod
    def get_json(url: str) -> JSON:
        """
        :param url: str:
        :return: JSON
        """
        headers = {
            'Accept': "*/*",
            'User-Agent': ("Mozilla/5.0 (Windows NT 6.1) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/107.0.5304.88 Safari/537.36"),
        }
        try:
            response = requests.get(url=url, headers=headers)
            return response.json()
        except ConnectionError as conn_ex:
            logger.error(conn_ex)

    def execute(self, urls: dict) -> dict:
        """
        collect data in threads and save to dictionary
        :param urls: list:
        :return: dict{page: data}
        """
        result = {}
        with ThreadPoolExecutor() as executor:
            future = {
                executor.submit(self.get_json, url):
                    page for page, url in urls.items()
            }
            for data in as_completed(future):
                page = future[data]
                result[page] = data.result()
        return result

    @staticmethod
    def check_item(data: JSON, id: int) -> str:
        """
        Check if item on page (single search)
        :param data: JSON
        :param id: int
        :return: str
        """
        for position, item in enumerate(data['data']['products'], start=1):
            if item['id'] == id:
                return (f'{item["name"]} \n'
                        f'Позиция: {position}')

    @staticmethod
    def check_item_multy(data: JSON, id_s: list) -> dict:
        """
        Check if item on page (multy search)
        :param data: JSON
        :param id_s: list
        :return: dict{id: name, position}
        """
        result = {}
        for position, item in enumerate(data['data']['products'], start=1):
            if item['id'] in id_s:
                result[item['id']] = position
                # можно так f'Название: {item["name"]}, Позиция: {position}'
                # но не очень красивый вывод получается
        return result

    def find_single(self, data: dict, id: int) -> str:
        """
        Check for items on all 100 pages (for single search)
        :param data: dict
        :param id: int
        :return: str
        """
        for page, information in data.items():
            if information != {}:
                result = self.check_item(information, id)
                if result:
                    answer = f'{result}, Страница: {page}'
                    return answer

    def find_multy(self, data: dict, id_s: list) -> dict[any, dict]:
        """
        Check for items on all 100 pages (for multy search)
        :param data: dict
        :param id_s: list
        :return: dict{int: dict}
        """
        founded = {}
        for page, information in data.items():
            if information != {}:
                result = self.check_item_multy(information, id_s)
                if result:
                    founded[page] = result
        return founded

    @staticmethod
    def get_id_list(id_s: str):
        """
        get list[id] from str(query)
        :param id_s: str
        :return: list[id]
        """
        id_list = [int(i) for i in id_s.split('/')]
        logger.info(id_list)
        return id_list

    def single_search(self, data: dict, id: int) -> str:
        """
        :param data: dict
        :param id: int
        :return: str
        """
        result = self.find_single(data, id)
        if not result:
            logger.info(f'No item with id {id}')
            return 'Не найдено'
        return result

    def multy_search(self, data: dict, id_s: str) -> dict:
        """
        :param data: dict
        :param id_s: str
        :return: dict
        """
        id_list = self.get_id_list(id_s)
        result = self.find_multy(data, id_list)
        logger.info(type(result))
        return result

    def main(self, query_text: str) -> str | dict:
        """
        :param query_text: str
        :return: str | dict
        """
        id, query = query_text.split(' ', maxsplit=1)
        logger.info(f'Get request - (id: {id}, query: {query})')
        start = time.time()
        urls = self.get_urls(query)
        data = self.execute(urls)
        if '/' in query_text:
            result = self.multy_search(data, id)
        else:
            result = self.single_search(data, int(id))
        logger.info(f'Answer: {result}')
        logger.info('Execute time: {:.02f}s.'.format(time.time() - start))
        return result
