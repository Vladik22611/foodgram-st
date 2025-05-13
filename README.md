
#  Продуктовый помощник - Фудграм

[![GitHub - Test status](https://github.com/Vladik22611/foodgram-st/actions/workflows/main.yml/badge.svg)](https://github.com/Vladik22611/foodgram-st/actions?query=workflow:MainFoodgramworkflow)

## Стек технологий

[![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django-REST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/ru/)
[![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

## Описание

Foodgram — Ваш кулинарный цифровой помощник

- Публикуйте рецепты — Делитесь своими кулинарными шедеврами с сообществом
- Подписывайтесь на авторов — Следите за теми, чьи рецепты вас вдохновляют
- Сохраняйте в «Избранное» — Создайте персональную кулинарную книгу из понравившихся рецептов
- Умный список покупок — Генерируйте персональный shopping_list в формате .txt с ингредиентами для выбранных блюд

## Запуск

```shell
# Склонировать репозиторий
git clone https://github.com/Vladik22611/foodgram-st.git
```

> [!IMPORTANT]
> Для работы PostgreSQL необходимо создать файл `.env` с переменными окружения в корневой директории проекта.  
> Пример файла [./.env.example](https://github.com/Vladik22611/foodgram-st/blob/main/.env.example)

> [!IMPORTANT]
> Для дальнейшей работы понадобится Docker.  
> Его можно установить с официального [сайта](https://www.docker.com/products/docker-desktop).

1. Перейти в директорию ./infra
```shell
# Перейти в директорию /infra из корневой
cd infra
```

2. Запуск (из директории /infra при активном Docker):
   
```shell
# Собрать образы и запустить контейнеры 
docker-compose up --build
```
> [!WARNING]
> При запуске контейнеров БД автоматически заполнится данными ингредиентов из [./backend/data](https://github.com/Vladik22611/foodgram-st/tree/main/backend/data)


3. Создание суперпользователя
```shell
# в директории /infra
docker-compose exec foodgram_backend python manage.py createsuperuser
```

### Админ-зона и документация

- [Админ-зона](http://localhost:8000/admin/)
- [Документация](http://localhost:8000/api/docs/)

## GitHub Actions

### Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:

```
DOCKER_USERNAME         - логин Docker Hub
DOCKER_PASSWORD         - пароль от Docker Hub
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение
```

### После каждого обновления репозитория (push в main ветку) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета ruff)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Отправка сообщения в Telegram в случае успеха

## Автор:

Гречкин Владсислав  

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/g_vladislav22)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Vladik22611)
