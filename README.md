![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

# Foodgram - продуктовый помощник 

Foodgram - это онлайн-сервис для любителей готовить. Пользователи данного сервиса могут публиковать рецепты, делиться рецептами друг с другом, добавлять понравившиеся рецепты в избранное и следить за обновлениями других пользователей. Также Foodgram сможет подсчитать для Вас необходимое количество ингредиентов всех выбранных блюд и составить из них список покупок, который можно скачать и взять с собой в магазин.

### Как запустить проект в контейнерах локально:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Aleksentcev/foodgram-project-react.git
```

```
cd foodgram-project-react/infra
```

Установить Docker Desktop на Ваш компьютер и запустить его.

Создать директории infra файл .env и заполнить его своими данными:

```
POSTGRES_DB=write_anything
POSTGRES_USER=write_username
POSTGRES_PASSWORD=write_password
DB_NAME=write_anything
DB_HOST=kitty_db
DB_PORT=1234
SECRET_KEY=your_secret_code
ALLOWED_HOSTS=localhost you_can_add_your_domain_here
```

Запустить оркестр контейнеров:

```
docker compose up
```

Дождаться сборки и запуска всех контейнеров и в другом окне терминала выполнить миграции:

```
docker compose exec backend python manage.py migrate 
```

Собрать и скопировать статику Django

```
docker compose exec backend python manage.py collectstatic
```
```
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/ 
```

Проект будет или не будет доступен по адресу: http://localhost/
Если ничего не заработало - идите пить чай :)

### Автор:

Михаил Алексенцев
[![Telegram](https://img.shields.io/badge/Telegram-aleksentcev-white?labelColor=blue&style=flat&link=https://t.me/aleksentcev)](https://t.me/aleksentcev)
