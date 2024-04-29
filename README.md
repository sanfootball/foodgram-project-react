сервер https://foodgram-diplom.webhop.me/

админ логин: example@mail.ru(email)

пароль: admin

Документация API: https://foodgram-diplom.webhop.me/api/docs/

# Проект "Foodgram"


## Описание

Проект "Foodgram" - это онлайн-сервис и API для него. Этот проект был разработан студентом Яндекс.Практикум, Трубниковым Александром, в рамках дипломной работы. Сервис позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, а также создавать списки покупок для рецептов.

## Функциональность

Проект предоставляет следующую функциональность:

- Аутентификация пользователей с использованием модуля DRF - Authtoken.
- Создание объектов разрешено только аутентифицированным пользователям. Для некоторых действий также установлены ограничения, связанные с ролями и авторством.
- Для неаутентифицированных пользователей доступ к API только на уровне чтения.
- Управление пользователями, возможность редактировать свой профиль.
- Возможность подписываться на других пользователей и отписываться от них.
- Получение списка всех рецептов, их добавление, обновление и удаление.
- Возможность добавить рецепт в избранное.
- Создание списка покупок и скачивание его в формате PDF.
- Получение списка всех тегов и ингредиентов.
- Фильтрация рецептов по различным параметрам.

## Документация API

Документация к API доступна по адресу [https://foodgram-diplom.webhop.me/api/docs/](https://foodgram-diplom.webhop.me/api/docs/).

## Технологии

Проект использует следующие технологии:

- Python 3.7
- Django 3.2.15
- Django Rest Framework 3.12.4
- Authtoken
- Docker
- Docker-compose
- PostgreSQL
- Gunicorn
- Nginx
- GitHub Actions
- Выделенный сервер Linux Ubuntu 22.04 с публичным IP

## Локальный запуск проекта

Для локального запуска проекта выполните следующие шаги:

- Склонируйте репозиторий:

```bash
git clone <название репозитория>
cd <название репозитория>
```
### Установка и настройка проекта

- Создайте и активируйте виртуальное окружение:

   Для Mac или Linux:

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
   Для Windows:
  
   ```bash
 
   python -m venv venv
   source venv/Scripts/activate
   ```
   
- Создайте .env файл с переменными окружения:
  ```bash
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=<имя базы данных postgres>
   DB_USER=<пользователь бд>
   DB_PASSWORD=<пароль>
   DB_HOST=db
   DB_PORT=5432
  ```
- Запустите контейнеры Docker:
  
  ```bash
  
  docker-compose up
  ```
- Установите зависимости из файла requirements.txt:

  ```bash

  cd ..
  cd backend
  pip install -r requirements.txt
  ```
- Примените миграции:

   ```bash
   python manage.py migrate
   ```
- Заполните базу тестовыми данными об ингредиентах:

   ```bash
  - python manage.py ingredients_in_data
   ```

### Локальный запуск проекта (продолжение)

- Создайте суперпользователя, если это необходимо:

    ```bash
    python manage.py createsuperuser
    ```

- Запустите локальный сервер:

    ```bash
    python manage.py runserver
    ```

## Установка на удалённом сервере

Для развертывания проекта на удаленном сервере выполните следующие шаги:

1. Выполните вход на удаленный сервер.

2. Установите Docker:

   ```bash
   sudo apt install docker.io
   ```

3. Установите Docker-compose:
  
   ```bash
   sudo apt install docker-compose     
   ```
Можно также воспользоваться официальной инструкцией.

- Находясь локально в директории infra, скопируйте файлы docker-compose.yml и nginx.conf на удаленный сервер:
  ```
  scp docker-compose.yml <username>@<host>:/home/<username>/
  scp nginx.conf <username>@<host>:/home/<username>/
  ```
- Для правильной работы workflow необходимо добавить в Secrets данного репозитория на GitHub переменные окружения:
  
   Переменные PostgreSQL, ключ проекта Django и их значения по-умолчанию можно взять из файла `.env.example`, затем установить свои.
   ```
   DOCKER_USERNAME=<имя пользователя DockerHub>
   DOCKER_PASSWORD=<пароль от DockerHub>
   
   USER=<username для подключения к удаленному серверу>
   HOST=<ip сервера>
   PASSPHRASE=<пароль для сервера, если он установлен>
   SSH_KEY=<ваш приватный SSH-ключ (для получения команда: cat ~/.ssh/id_rsa)>
   
   TELEGRAM_TO=<id вашего Телеграм-аккаунта>
   TELEGRAM_TOKEN=<токен вашего бота>
   ```
   
## Workflow проекта

Workflow проекта запускается при выполнении команды git push и включает следующие этапы:

 - `tests:` проверка кода на соответствие PEP8.
 - `build_and_push_to_docker_hub:` сборка и размещение образа проекта на DockerHub.
 - `deploy:` автоматический деплой на боевой сервер и запуск проекта.
 - `send_massage:` отправка уведомления пользователю в Телеграм.

## После успешного запуска

### После успешного завершения workflow, проект будет доступен на боевом сервере. Для завершения настройки выполните следующие действия:

  - Примените миграции:
   ```
   sudo docker-compose exec backend python manage.py migrate
   ```
  - Подгрузите статику:
  ```
  sudo docker-compose exec backend python manage.py collectstatic --no-input
  ```
  - Заполните базу тестовыми данными об ингредиентах:
  ```
  sudo docker-compose exec backend python manage.py load_ingredients_data
  ```
  - Создайте суперпользователя:
  ```
  sudo docker-compose exec backend python manage.py createsuperuser
  ```

## Примеры некоторых запросов к API:

  - Регистрация пользователя:
  ```
  POST /api/users/
  ```
 - Получение данных своей учетной записи:
 ```
 GET /api/users/me/ 
 ```
 - Добавление подписки:
 ```
 POST /api/users/id/subscribe/
 ```
 - Обновление рецепта:
 ```
 PATCH /api/recipes/id/
 ```
 - Удаление рецепта из избранного:
 ```
 DELETE /api/recipes/id/favorite/
 ```
 - Получение списка ингредиентов:
 ```
 GET /api/ingredients/
 ```
 - Скачать список покупок:
 ```
 GET /api/recipes/download_shopping_cart/
 ```

## Пример работы проекта

### Проект доступен по адресу: http://foodgram-diplom.myddns.me/

### Для доступа в админку используйте следующие данные:

 - email - example@mail.ru
 - пароль - admin

Аккаунт пользователя:

## Автор
Трубников Александр    
email: petrovskii1980@mail.ru  
Telegram: https://t.me/sanfootball
