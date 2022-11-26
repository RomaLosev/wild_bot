import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union

import requests
from loguru import logger

logger.add("logger_finder.log", enqueue=True)
JSON = Union[dict[str, any]]


class Finder:

    @staticmethod
    def get_urls(query: str) -> dict:
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
        headers = {
            'Accept': "*/*",
            'User-Agent': ("Mozilla/5.0 (Windows NT 6.1) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/107.0.5304.88 Safari/537.36"),
        }
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except ConnectionError as conn_ex:
            logger.error(conn_ex)

    def execute(self, urls: dict) -> dict:
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
        for position, item in enumerate(data['data']['products'], start=1):
            if item['id'] == id:
                return (f'{item["name"]} \n'
                        f'Позиция: {position}')

    def find_single(self, data: dict, id: int) -> str:
        for page, information in data.items():
            if information != {}:
                result = self.check_item(information, id)
                if result:
                    answer = f'{result}, Страница: {page}'
                    return answer

    @staticmethod
    def check_item_multy(data: JSON, id_s: list) -> dict:
        result = {}
        for position, item in enumerate(data['data']['products'], start=1):
            if item['id'] in id_s:
                result[item['id']] = f'{item["name"]}, Позиция: {position}'
        return result

    def find_multy(self, data: dict, id_s: list) -> dict[any, dict]:
        founded = {}
        for page, information in data.items():
            if information != {}:
                result = self.check_item_multy(information, id_s)
                if result:
                    founded[page] = result
        return founded

    @staticmethod
    def get_id_list(id: str):
        id_list = [int(i) for i in id.split('/')]
        logger.info(id_list)
        return id_list

    def main(self, text: str) -> str:
        id, query = text.split(' ', maxsplit=1)
        logger.info(f'Get request - (id: {id}, query: {query})')
        start = time.time()
        urls = self.get_urls(query)
        data = self.execute(urls)
        if '/' in text:
            id_list = self.get_id_list(id)
            result = self.find_multy(data, id_list)
        else:
            result = self.find_single(data, int(id))
        if not result:
            logger.info(f'No item with id {id} and name {query}')
            return 'Не найдено'
        logger.info(f'Answer: {result}')
        logger.info(f'execute time: {time.time()-start}s.')
        return result
