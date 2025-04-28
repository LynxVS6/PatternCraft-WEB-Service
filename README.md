# PatternCraft-WEB-Service

## 🚀 Быстрый старт

1. **Клонировать репозиторий:**
   ```bash
   git clone <URL репозитория>
   cd PatternCraft-WEB-Service
   ```

2. **Создать и активировать виртуальное окружение:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Установить зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Создать файл `.env` по шаблону:**
   ```bash
   cp .env.template .env
   ```
   Заполнить переменные (SECRET_KEY, SECURITY_PASSWORD_SALT, SMTP-данные).

5. **Запустить миграции БД:**
   ```bash
   flask db upgrade
   ```

7. **Запустить приложение:**
   ```bash
   flask --app app run
   ```
   Далее сервер будет доступен по адресу <http://127.0.0.1:5000>
