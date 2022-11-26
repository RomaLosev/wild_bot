from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union

import requests
from loguru import logger

logger.add("logger_finder.log", enqueue=True)
JSON = Union[dict[str, any]]


class Finder:

    @staticmethod
    def get_urls(query: str) -> list:
        urls = []
        for page in range(1, 101):
            urls.append(f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&'
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
                            f'regions=80,64,83,4,38,33,70,82,69,68,86,75,30,40,48,1,22,66,31,71&'
                            f'resultset=catalog&'
                            f'sort=popular&'
                            f'spp=0&'
                            f'suppressSpellcheck=false')
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

    @staticmethod
    def check_items(data: JSON, id: int) -> str:
        for position, item in enumerate(data['data']['products'], start=1):
            if item['id'] == id:
                return (f'{item["name"]} \n'
                        f'Позиция: {position}')

    def execute(self, urls: list) -> dict:
        result = {}
        with ThreadPoolExecutor() as executor:
            future = {
                executor.submit(self.get_json, url):
                    page for page, url in enumerate(urls, start=1)
            }
            for data in as_completed(future):
                page = future[data]
                result[page] = data.result()
        return result

    def find(self, data: dict, id: int) -> str:
        for page, information in data.items():
            if information != {}:
                result = self.check_items(information, id)
                if result:
                    answer = f'{result}, Страница: {page}'
                    return answer

    def main(self, id: int, query: str) -> str:
        logger.debug(f'id: {id}, query: {query}')
        urls = self.get_urls(query)
        data = self.execute(urls)
        result = self.find(data, id)
        logger.info(result)
        return result
