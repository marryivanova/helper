# 📘 Pytest Шпаргалка

**Пример unit test:** `\src\abc_expl\test`

## 🔧 Установка и запуск

```bash
pip install pytest

pytest                          # все тесты
pytest tests/                   # папка
pytest test_file.py             # файл
pytest -k "login"               # по имени (фильтр)
pytest -m slow                  # по маркеру
pytest -v                       # подробно
pytest -x                       # стоп при первой ошибке
pytest --maxfail=3              # стоп после 3 ошибок
pytest -n auto                  # параллельно (xdist)
pytest --cov=myapp              # покрытие (cov)
pytest --tb=short               # короткий трейсбек
pytest --durations=5            # 5 самых медленных тестов
```

---

## 📁 Структура тестов

```python
# Файлы: test_*.py или *_test.py
# Функции: test_*
# Классы: Test* (без __init__)

def test_example():
    assert 1 + 1 == 2

class TestUser:
    def test_name(self):
        user = User("Alice")
        assert user.name == "Alice"
```

---

## ✅ Assertions (утверждения)

```python
assert x == 5
assert x > 0
assert "hello" in text
assert result is None
assert isinstance(obj, MyClass)
assert obj in container
```

### Проверка исключений

```python
with pytest.raises(ZeroDivisionError):
    divide(1, 0)

with pytest.raises(ValueError, match="не может быть отрицательным"):
    process(-5)
```

---

## 🧩 Фикстуры (Fixtures)

```python
import pytest

@pytest.fixture
def user():
    return {"name": "Alice", "age": 30}
```

### Уровни видимости

```python
@pytest.fixture(scope="function")   # по умолчанию, для каждого теста
@pytest.fixture(scope="class")      # один раз на класс
@pytest.fixture(scope="module")     # один раз на файл
@pytest.fixture(scope="session")    # один раз на всю сессию
```

### Автоиспользование

```python
@pytest.fixture(autouse=True)
def setup_logging():
    print("Setup")
    yield
    print("Teardown")
```

### Зависимости фикстур

```python
@pytest.fixture
def db():
    return Database()

@pytest.fixture
def user_repo(db):      # db подставляется автоматически
    return UserRepository(db)
```

---

## 📊 Параметризация

```python
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Несколько параметров (декартово произведение)

```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    assert multiply(x, y) == x * y   # 4 комбинации
```

---

## 🏷️ Маркеры (Marks)

```python
@pytest.mark.slow
def test_heavy():
    pass

@pytest.mark.smoke
def test_login():
    pass
```

### Запуск по маркерам

```bash
pytest -m smoke          # только smoke
pytest -m "not slow"     # все кроме slow
```

### Пропуск теста

```python
@pytest.mark.skip(reason="ещё не готово")
def test_future():
    pass

@pytest.mark.skipif(sys.version_info < (3, 8), reason="требуется Python 3.8+")
def test_new():
    pass
```

### Ожидаемое падение

```python
@pytest.mark.xfail(reason="известный баг")
def test_bug():
    pass
```

---

## 🎁 Встроенные фикстуры

### Временные файлы/папки

```python
def test_tmp(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    f = d / "file.txt"
    f.write_text("hello")
    assert f.read_text() == "hello"
```

### Переменные окружения

```python
def test_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "123")
    assert os.getenv("API_KEY") == "123"
```

### Перехват вывода (stdout/stderr)

```python
def test_output(capsys):
    print("Hello")
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"
```

### Перехват логов

```python
def test_logs(caplog):
    import logging
    logging.warning("test")
    assert "test" in caplog.text
```

---

## 📦 conftest.py

Структура проекта:

```
project/
├── conftest.py          # глобальные фикстуры
├── tests/
│   ├── conftest.py      # локальные фикстуры
│   ├── test_users.py
│   └── test_products.py
```

Пример `conftest.py`:

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: быстрая проверка")
```

---

## 🧪 Утилиты

### Заморозка времени (freezegun)

```python
from freezegun import freeze_time

@freeze_time("2024-01-01")
def test_time():
    assert datetime.now().year == 2024
```

### Моки (unittest.mock)

```python
from unittest.mock import Mock, patch

def test_with_mock():
    mock = Mock()
    mock.get.return_value = {"status": "ok"}
    assert mock.get()["status"] == "ok"

@patch("module.external_api")
def test_api(mock_api):
    mock_api.return_value = 42
    assert module.func() == 42
```

---

## 🔌 Полезные плагины

Установка:

```bash
pip install pytest-xdist pytest-cov pytest-timeout pytest-html pytest-mock
```

| Плагин | Команда |
|--------|---------|
| xdist | `pytest -n auto` |
| cov | `pytest --cov=src --cov-report=html` |
| timeout | `pytest --timeout=5` |
| html | `pytest --html=report.html` |

---

## ❗ Частые ошибки

| ❌ Ошибка | ✅ Решение |
|-----------|-----------|
| Файл не `test_*.py` | Переименовать |
| Класс без `Test` | Добавить `Test` в начало |
| `__init__` в классе | Удалить `__init__` |
| Меняет глобальное состояние | Использовать фикстуры с `yield` |
| Слишком сложный тест | Разбить на несколько маленьких |

---

## 🧠 Паттерн AAA

```python
def test_discount():
    # Arrange (подготовка)
    user = User(role="VIP")
    product = Product(price=100)
    
    # Act (действие)
    result = calculate_discount(user, product)
    
    # Assert (проверка)
    assert result == 90
```

---

## ⚡ Быстрый старт с нуля

```bash
# 1. Создать проект
mkdir my_project && cd my_project
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate (Windows)

# 2. Установить pytest
pip install pytest pytest-cov

# 3. Создать тест
echo "def test_example(): assert 1 + 1 == 2" > test_example.py

# 4. Запустить
pytest -v --cov=.
```

# 📊 Allure - отчеты для тестов

## 🔗 Полезные ссылки

| Ресурс | Ссылка |
|--------|--------|
| Allure Pytest | [https://github.com/allure-framework/allure-pytest](https://github.com/allure-framework/allure-pytest) |
| Allure Docker Service UI | [https://github.com/fescobar/allure-docker-service-ui](https://github.com/fescobar/allure-docker-service-ui) |
| Документация по запуску | [https://github.com/fescobar/allure-docker-service-ui](https://github.com/fescobar/allure-docker-service-ui) |
| Скрипт отправки результатов | [https://github.com/fescobar/allure-docker-service/blob/master/allure-docker-api-usage/send_results.ps1](https://github.com/fescobar/allure-docker-service/blob/master/allure-docker-api-usage/send_results.ps1) |

---

## 🚀 Быстрый старт

### Установка Allure Pytest

```bash
pip install allure-pytest
```

### Запуск тестов с генерацией отчетов

```bash
pytest --alluredir=./allure-results
```

### Просмотр отчета локально

```bash
allure serve ./allure-results
```

---

## 🐳 Allure Docker Service

### Поднятие UI для отчетов

Полная инструкция описана здесь:
[https://github.com/fescobar/allure-docker-service-ui](https://github.com/fescobar/allure-docker-service-ui)

### Скрипт отправки результатов

Ссылка: https://github.com/fescobar/allure-docker-service/blob/master/allure-docker-api-usage/send_results.ps1
```powershell
# PowerShell скрипт для отправки результатов
Скрит кладем куда-нибудь и запускаем 
```

---

## ⚙️ Настройка Nginx для Allure

Пример конфигурации Nginx для проброса на Allure:

```nginx
events {
    worker_connections 1024;
}

http {
    # Редирект с HTTP на HTTPS
    server {
        listen 80;
        server_name allure-dev.lol.net;
        return 301 https://$host$request_uri;
    }

    # Основной сервер HTTPS
    server {
        listen 443 ssl;
        server_name allure-dev.lol.net;

        # SSL сертификаты
        ssl_certificate /etc/nginx/ssl/fullchain.crt;
        ssl_certificate_key /etc/nginx/ssl/cert.key;

        # Заголовки безопасности
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options "";

        # Прокси на Allure API
        location /api/allure-docker-service/ {
            proxy_pass http://allure:5050/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Authorization $http_authorization;
            proxy_hide_header X-Frame-Options;
            add_header X-Frame-Options "ALLOWALL" always;
        }

        # Прокси на Allure UI
        location / {
            proxy_pass http://allure-ui:5252;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_hide_header X-Frame-Options;
            add_header X-Frame-Options "";
        }
    }
}
```

---

## 📝 Основные возможности Allure

| Возможность | Описание |
|-------------|----------|
| 📊 Визуальные отчеты | Наглядное представление результатов тестов |
| 🏷️ Категоризация | Группировка тестов по функциям и компонентам |
| 📈 Графики и диаграммы | Визуализация трендов и статистики |
| 🔍 Детализация | Подробная информация по каждому тесту |
| 📎 Вложения | Добавление скриншотов, логов, файлов |
| 🔄 Интеграция | Поддержка CI/CD систем |

---

## 🏷️ Использование в коде

```python
import allure

@allure.feature("Авторизация")
@allure.story("Вход в систему")
@allure.severity(allure.severity_level.CRITICAL)
def test_login():
    with allure.step("Открыть страницу входа"):
        open_login_page()
    
    with allure.step("Ввести логин и пароль"):
        enter_credentials("user", "pass")
    
    with allure.step("Нажать кнопку входа"):
        click_login_button()
    
    allure.attach("Screenshot", "скриншот", attachment_type=allure.attachment_type.PNG)
    assert is_logged_in() == True
```

---

## 🎯 Полезные команды

```bash
# Генерация отчета
allure generate ./allure-results -o ./allure-report

# Открыть отчет
allure open ./allure-report

# Очистить результаты
rm -rf ./allure-results

# Запуск с очисткой
pytest --alluredir=./allure-results --clean-alluredir
```