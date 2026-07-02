# 🚀 Инструкция по развертыванию проекта

[⬅ На главную](README.md)

---

## 1. Быстрый старт (Настройка окружения)

Перед началом разработки необходимо создать и активировать виртуальное окружение:

### Создание и активация
```bash
# Создание venv
python -m venv venv

# Активация на Linux/macOS
source venv/bin/activate

# Активация на Windows
.\venv\Scripts\activate
```

Установка зависимостей
Проект использует Poetry для управления зависимостями.

```bash
Установите Poetry (если еще не установлено): pip install poetry

Установите все зависимости проекта: poetry install
```
2. Работа с зависимостями (Poetry)
Poetry автоматизирует создание poetry.lock и управление версиями. Используйте следующие команды в директории проекта:

Добавление новой библиотеки

```bash
# Добавить обычную зависимость
poetry add <имя_библиотеки>

# Добавить зависимость только для разработки (тесты, линтеры)
poetry add <имя_библиотеки> --group dev
Удаление библиотеки

poetry remove <имя_библиотеки>
Обновление зависимостей

# Обновить все пакеты согласно условиям в pyproject.toml
poetry update

# Обновить конкретный пакет
poetry update <имя_библиотеки>
```

Пример toml.
```yaml
[tool.poetry]
name = "Тут имя"
version = "0.1.0"
description = ""
authors = ["Тут имя и почту"]

[tool.poetry.dependencies]
python = "^3.9.2"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
python-multipart = "^0.0.6"
celery = "^5.3.6"
jinja2 = "^3.1.2"
httpx = "^0.25.0"
aiofiles = "^24.1.0"
loguru = "^0.7.0"
itsdangerous = "^2.2.0"
PyJWT = "^2.8.0"
bitrix24-python3-client = "^0.4.0"
sentry-sdk = "^1.34.0"
starlette = "^0.49.1"
python-dotenv = "^1.0.0"
fastapi = ">=0.109.1"
requests = ">=2.28.1"
SQLAlchemy = ">=1.4.35"
PyMySQL = ">=1.0.2"
redis = ">4.5.5"
mysql-connector-python = ">8.0.23"
tenacity = "^8.0.0"
PyBitrix = "^1.1.4"
apscheduler = "^3.10.0"
Babel = "^2.14.0"
sendgrid = "^6.12.5"
watchdog = {extras = ["watchmedo"], version = "^4.0.0"}
uvicorn = {extras = ["standard"], version = ">=0.24.0"}

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 120
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  | \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
]

[tool.pytest.ini_options]
addopts = "--disable-warnings"
filterwarnings = [
    "ignore::pydantic.warnings.PydanticDeprecatedSince20",
    "ignore::DeprecationWarning"
]
asyncio_mode = "auto"
```

3. Настройка конфигурации проекта
Файл pyproject.toml содержит не только зависимости, но и настройки инструментов разработки:

- Black: Форматирование кода (лимит 120 символов).
- Pytest: Автоматически установлен режим asyncio, игнорируются предупреждения DeprecationWarning.
- Coverage: Настроено исключение файлов миграций и тестов из отчетов о покрытии кода.
Если нужно изменить версию Python или добавить специфический драйвер, редактируйте секцию [tool.poetry.dependencies].
После любых правок в файле pyproject.toml вручную, выполните poetry lock --no-update, чтобы синхронизировать файл блокировки версий.

4. Конфигурация запуска
Убедитесь, что после установки зависимостей у вас настроен файл .env.

Создайте его на основе примера: `cp .env.example .env`
(Заполните переменные окружения: БД, ключи API, токены Sentry и т.д.)

Запуск приложения (через Poetry): `poetry run uvicorn src.main:app --reload`


## 🎨 Наведение порядка в коде и документации

Чтобы код был чистым, а документация актуальной, выполняйте эти шаги по порядку:

### 1. Форматирование кода
Сначала приводим стиль кода к общему стандарту:

* **Black:** Форматирует код и задает длину строки 100 символов.
  ```bash
  black --line-length 100 .
  isort: Сортирует импорты библиотек в алфавитном порядке (лучше устанавливать через poetry add isort --group dev).
  isort .
  ```
2. Генерация документации
Для создания автоматической документации проекта используйте следующие инструменты:

Вариант A: Через pdoc / pydoc-markdown
Если вы хотите сформировать документацию на основе файлов проекта:

```bash
# Установка
pip install pdoc pydoc-markdown
```
# Генерация

pydoc-markdown -m yandex-context > README.md
Вариант B: Через Lazydocs (более продвинутый)
Создает полноценную структуру папки docs/ с удобной навигацией:

```bash
# Установка
pip install lazydocs
# Генерация документации для модуля yandex-context в папку docs
lazydocs --output-path ./docs ./yandex-context
```
Совет: Лучше всего добавить эти команды в системные скрипты или Makefile, чтобы не вводить их каждый раз вручную.

```bash
.PHONY: help install format lint generate-docs clean

# Помощь по доступным командам
help:
	@echo "Доступные команды:"
	@echo "  make install      - установка всех зависимостей"
	@echo "  make format       - форматирование кода (black + isort)"
	@echo "  make generate-docs - генерация документации через lazydocs"
	@echo "  make clean        - очистка кэша и временных файлов"

# Установка зависимостей
install:
	poetry install

# Наведение красоты (Black + Isort)
format:
	@echo "Formatting code..."
	black --line-length 100 .
	isort .

# Генерация документации
generate-docs:
	@echo "Generating documentation..."
	lazydocs --output-path ./docs ./имя папки проекта

# Очистка проекта (удаление кэшей Python)
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .coverage
```

**Как пользоваться этим Makefile:**
Чтобы запустить команду, просто введите в терминале:

```bash
make format — автоматически запустит Black и Isort.
make generate-docs — запустит генерацию документации в папку docs.
make install — установит окружение.
```