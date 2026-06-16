# Трекер полезных привычек

Бэкенд-часть SPA веб-приложения для трекинга полезных привычек.

## 🚀 Запуск с Docker

```bash
# Копирование переменных окружения
cp .env.example .env

# Запуск всех сервисов
docker-compose up -d

# Выполнение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser