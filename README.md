<h1 align="center">"Продуктовый помощник - Фудграм"</h1>

<p align="center">
    <a href="https://github.com/Vladik22611/foodgram-st/actions?query=workflow:main.yml">
        <img alt="GitHub - Test status" src="https://github.com/Vladik22611/foodgram-st/actions/workflows/main.yml/badge.svg">
    </a>
</p>

<h2 align="center">Стек технологий</h2>

<p align="center">
    <a href="https://www.djangoproject.com/">
        <img alt="Django" src="https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white">
    </a>
    <a href="https://www.django-rest-framework.org/">
        <img alt="Django-REST-Framework" src="https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray">
    </a>
    <a href="https://www.postgresql.org/">
        <img alt="PostgreSQL" src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white">
    </a>
    <a href="https://nginx.org/ru/">
        <img alt="Nginx" src="https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white">
    </a>
    <a href="https://gunicorn.org/">
        <img alt="gunicorn" src="https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white">
    </a>
    <a href="https://www.docker.com/">
        <img alt="docker" src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white">
    </a>
</p>

<h2 align="center">Описание</h2>

<p>
  Foodgram — Ваш кулинарный цифровой помощник

🍲 Публикуйте рецепты — Делитесь своими кулинарными шедеврами с сообществом

❤️ Подписывайтесь на авторов — Следите за теми, чьи рецепты вас вдохновляют

📌 Сохраняйте в «Избранное» — Создайте персональную кулинарную книгу из понравившихся рецептов

🛒 Умный список покупок — Генерируйте персональный shopping_list в формате .txt с ингредиентами для выбранных блюд
</p>

<h2 align="center">Запуск</h2>

```shell
# Склонировать репозиторий
git clone https://github.com/Vladik22611/foodgram-st.git
```

> [!IMPORTANT]
> Для работы PostgreSQL необходимо создать файл `.env` с переменными окружения в корневой директории проекта.</br>
> Пример файла [./.env.example](https://github.com/Vladik22611/foodgram-st/blob/main/.env.example)

> [!IMPORTANT]
> Для дальнейшей работы понадобится Docker.</br>
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

<h3>
    <a href="http://localhost:8000/admin/">Админ-зона</a><p></p>
    <a href="http://localhost:8000/api/docs/">Документация</a>
</h3> 

<h2 align="center">GitHub Actions</h2>

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

Гречкин Владсислав <br>

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/g_vladislav22)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Vladik22611)
