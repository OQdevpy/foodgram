Проект FoodGram Recipe
Это блог для обмена рецептами разными поварами и любителями готовки.
На сайте люди могут зарегистрироваться и быть полноценной частью проекта. 
Пользователи смогут подписываться на друг друга, обмениваться рецептами, добавлять 
рецепты в избранное, а также добавлять любимые рецепты в список покупок.

Технологии  и инструменты, использованные в разработке этого проекта:
Python
Django Rest Framework
Docker
Nginx
Postgres
GitHub
DockerHub
Postman


Клонировать репозиторий и перейти в папку backend:
1. git clone git@github.com:YanSv15/foodgram-project-react.git
2. cd backend/foodgram
Создать и активировать виртуальное окружение:
3. python -m venv venv
4. source venv/bin/activate
Установить зависимости из файла requirements.txt:
5. pip install -r requirements.txt
Выполнить миграции:
6. python manage.py migrate
Загрузить ингридиенты из csv-файла:
7. python manage.py loaddata dump.json


Заполнение .env файла:
SECRET_KEY
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

