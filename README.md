Проект FOODGRAM

Foodgram - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект доступен по ссылке http://foodgram-final.ddns.net

Стек:
Python
Django
Docker
Nginx
PostgresQL
Gunicorn
React

Как развернуть проект:

1. Клонировать репозиторий
git@github.com:np-dvs/foodgram-project-react.git

2. В директории проекта создайте файл .env с вашими данными по примеру файла env_example. 

3. Перейдите в директорию infra - cd infra/

4. Запустите файл оркестрации командой 
docker compose -f docker-compose.production.yml up -d

5. Последовательно выполните команды для применения миграций и сборки статики
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/

6. Для наполнения БД ингредиентами - выполните команду
docker compose -f docker-compose.production.yml exec backend python manage.py csv_import

УСПЕХ :) 

Автор - Кудрявцева Анастасия