## REST API для Справочника Организаций

Это REST API приложение, построенное на FastAPI, Pydantic, SQLAlchemy и Alembic для управления справочником организаций, зданий и видов деятельности.

### Настройка и Запуск

1. Скопируйте `.env.example` в `.env` и заполните значения:
   ```ini
   DATABASE_URL=postgresql://user:password@db/app_db
   API_KEY=your_secret_key_here
   ```

2. Установите Docker и Docker Compose

3. Запустите сервисы:
   ```bash
   docker-compose up -d
   ```

 4. Инициализация базы данных:
   - Войдите в контейнер приложения: ```docker-compose exec app bash```
   - Примените миграции Alembic: ```alembic upgrade head```
   - Загрузите тестовые данные: ```python scripts/seed.py```

5. Документация
```http://127.0.0.1:8000/redoc```