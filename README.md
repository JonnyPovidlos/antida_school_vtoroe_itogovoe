# Инструкция
1. Создать виртуальное окружение
2. Установить переменные окружения в .env
    пример для linux:  
    + `FLASK_APP="./src/app.py"`
    + `SECRET_KEY="some_secret_key"`
3. Установить записимости   
    `pip install -r requirements.txt`
4. `flask run`
#Примечания
+ Фильтрация по тегам: у объявления должны быть все теги указанные в строке запроса

