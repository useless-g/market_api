pip install flask
pip install flask-http-auth
pip install pymongo

Для работы с api необходимо авторизоваться, так как это RESTful api, то логин и пароль нужно отправлять в запросе каждый раз.
login: design
password: smart

Запуск бд: mongod
Команда для запуска сервиса из папки проекта:  python ./main.py

Примеры curl команд для демонстрации функционала:

Получить все записи со всей информацией (вместо индекса передается сразу uri):
curl -u design:smart -i http://localhost:5000/market/api/v1.0/products

Получить всю информацию о товаре по индексу (вместо индекса передается сразу uri):
curl -u design:smart -i http://localhost:5000/market/api/v1.0/products/2

Получить список названий товаров (поиск по названиям, содержащим искомую фразу):
curl -u design:smart -i -H "Content-Type: application/json" -X GET -d '{"title": "iphone"}' http://localhost:5000/market/api/v1.0/filter_products

Добавить новый товар с переданными параметрами:
curl -u design:smart -i -H "Content-Type: application/json" -X POST -d '{"title":"iphone 3", "parameters": [
["price", 110000],
["weight", 240],
["diagonal", 10]
]}' http://localhost:5000/market/api/v1.0/products

Обновить запись по  индексу введенными параметрами:
curl -u design:smart -i -H "Content-Type: application/json" -X PUT -d '{"parameters":[["price", 95000], ["amount", 40]]}' http://localhost:5000/market/api/v1.0/products/2

Удалить запись по индексу:
curl -u design:smart -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/market/api/v1.0/products/2

Получить список названий товаров (поиск по параметрам, любое количество и любой порядок параметров):
curl -u design:smart -i -H "Content-Type: application/json" -X GET -d '{"parameters": [
["price", 90000],
["weight", 240],
["diagonal", 10]
]}' http://localhost:5000/market/api/v1.0/filter_products


curl команды с нужными параметрами для прохождения тестового сценария:
* создать товар
* найти его по параметру
* получить детали найденного товара

curl -u design:smart -i -H "Content-Type: application/json" -X POST -d '{"title":"iphone 3", "parameters": [
["price", 111000],
["weight", 240],
["diagonal", 10]
]}' http://localhost:5000/market/api/v1.0/products

curl -u design:smart -i -H "Content-Type: application/json" -X GET -d '{"parameters": [
["price", 111000]
]}' http://localhost:5000/market/api/v1.0/filter_products

curl -u design:smart -i http://localhost:5000/market/api/v1.0/products/1

