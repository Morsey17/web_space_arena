# Используем легкий образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы проекта
COPY . .

# Убедимся что папка ssl создана и файлы скопированы
RUN mkdir -p /app/ssl
COPY ssl/ /app/ssl/

# Проверка (для отладки)
#RUN ls -la /app/ssl/ && echo "SSL файлы должны быть здесь"

# Открываем порт 5000
EXPOSE 5000

# Команда запуска приложения
CMD ["python", "app.py"]

sudo docker run -d --name flask-game -p 5000:5000 --restart always flask-game