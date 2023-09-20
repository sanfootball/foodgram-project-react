сервер https://foodgram-diplom.webhop.me/

админ логин: example@mail.ru(email) пароль: admin

# Проект "Фудграм"


## Описание

Проект "Фудграм" - это онлайн-сервис и API для него. Этот проект был разработан студентом Яндекс.Практикум, Трубниковым Александром, в рамках дипломной работы. Сервис позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, а также создавать списки покупок для рецептов.

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

Документация к API доступна по адресу [http://localhost/api/docs/](http://localhost/api/docs/) после локального запуска проекта.

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
- Перейдите в директорию infra:
    
  ```bash
  cd infra
  ```
- Создайте файл .env по образцу:
  ```bash
  cp .env.example .env
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
  - python manage.py load_ingredients_data
   ```

### Локальный запуск проекта (продолжение)

- Создайте суперпользователя, если это необходимо:

    ```bash
    python manage.py createsuperuser
    ```

11. Запустите локальный сервер:

    ```bash
    python manage.py runserver
    ```

### Установка на удалённом сервере

Для развертывания проекта на удаленном сервере выполните следующие шаги:

1. Выполните вход на удаленный сервер.

2. Установите Docker:

   ```bash
   sudo apt install docker.io

sudo apt install docker.io
Установите Docker-compose:

sudo apt install docker-compose     
Можно также воспользоваться официальной инструкцией.

Находясь локально в директории infra, скопируйте файлы docker-compose.yml и nginx.conf на удаленный сервер:

scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
Для правильной работы workflow необходимо добавить в Secrets данного репозитория на GitHub переменные окружения:

Переменные PostgreSQL, ключ проекта Django и их значения по-умолчанию можно взять из файла .env.example, затем установить свои.

DOCKER_USERNAME=<имя пользователя DockerHub>
DOCKER_PASSWORD=<пароль от DockerHub>

USER=<username для подключения к удаленному серверу>
HOST=<ip сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш приватный SSH-ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<id вашего Телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
Workflow проекта
Workflow проекта запускается при выполнении команды git push и включает следующие этапы:

tests: проверка кода на соответствие PEP8.
build_and_push_to_docker_hub: сборка и размещение образа проекта на DockerHub.
deploy: автоматический деплой на боевой сервер и запуск проекта.
send_massage: отправка уведомления пользователю в Телеграм.
После успешного запуска
После успешного завершения workflow проект будет доступен на боевом сервере. Для завершения настройки выполните следующие действия:

Примените миграции:

sudo docker-compose exec backend python manage.py migrate
Подгрузите статику:

sudo docker-compose exec backend python manage.py collectstatic --no-input
Заполните базу тестовыми данными об ингредиентах:

sudo docker-compose exec backend python manage.py load_ingredients_data
Создайте суперпользователя:

sudo docker-compose exec backend python manage.py createsuperuser
Примеры некоторых запросов API
Примеры некоторых запросов к API:

Регистрация пользователя:

POST /api/v1/users/
Получение данных своей учетной записи:

GET /api/v1/users/me/ 
Добавление подписки:

POST /api/v1/users/id/subscribe/
Обновление рецепта:

PATCH /api/v1/recipes/id/
Удаление рецепта из избранного:

DELETE /api/v1/recipes/id/favorite/
Получение списка ингредиентов:

GET /api/v1/ingredients/
Скачать список покупок:

GET /api/v1/recipes/download_shopping_cart/
Пример работы проекта
Проект доступен по адресу: http://foodgram-diplom.myddns.me/

Для доступа в админку используйте следующие данные:

email - 
пароль - 
Аккаунт пользователя:

Автор
