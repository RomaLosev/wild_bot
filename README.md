# Описание

Тестовое задание
-

### Telegram бот для поиска товара по артикулу.

- Бот принимает на вход номенклатуру искомого товара и поисковый запрос
- В ответ присылает сообщение со страницей и позицией товара
- Есть возможность искать несколько номенклатур в одном поисковом запросе
```sh
{item_id search_query} Одиночный поиск

{item_id/item_id/... search_query} Поиск по нескльким артикулам
```

# Установка и запуск
**Зарегистрировать бота в [BotFather](https://t.me/BotFather)**

Клонировать репозиторий
```commandline
~ git clone git@github.com:RomaLosev/wild_bot.git
```
Создать файл .env и поместить туда телеграм токен
```commandline
~ touch .env
~ echo 'TELEGRAM_TOKEN=<your_token>' >> .env
```
Установить poetry
```commandline
~ pip install poetry
```
Установить зависимости
```commandline
~ poetry install
```
Собрать и запустить контейнер
```commandline
~ docker-compose up -d --build
```

# Бот готов к работе