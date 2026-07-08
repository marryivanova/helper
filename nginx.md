# 🌐 Nginx - Полное руководство

## 📚 Официальная документация

```
https://nginx.org/ru/
```

Неплохой гайд: https://selectel.ru/blog/install-nginx/
Тут можно взять примеры для конфигов: https://github.com/insspb/nginx-config
Пример: https://nginx.org/en/docs/example.html

в `helper\src\nginx` пример как настороить с https и автогенерацией сертификатов

---

## 🎯 Основная функциональность HTTP-сервера

### 📁 Обслуживание контента

| Функция | Описание |
|---------|----------|
| **Статические запросы** | Обслуживание статических файлов |
| **Индексные файлы** | Автоматическая отдача index.html, index.php и т.д. |
| **Список файлов** | Автоматическое создание списка файлов в директории |
| **Кэш дескрипторов** | Кэширование открытых файлов для ускорения |

### 🔄 Проксирование и балансировка

| Функция | Описание |
|---------|----------|
| **Reverse Proxy** | Акселерированное обратное проксирование с кэшированием |
| **Балансировка нагрузки** | Распределение трафика между серверами |
| **Отказоустойчивость** | Автоматическое переключение при сбоях |
| **FastCGI/uwsgi/SCGI** | Поддержка различных протоколов приложений |
| **Memcached** | Кэширование через memcached серверы |

### 🔧 Фильтры и обработка

| Функция | Описание |
|---------|----------|
| **Gzip сжатие** | Сжатие ответов для экономии трафика |
| **Byte-ranges** | Поддержка докачки файлов |
| **Chunked ответы** | Отправка данных частями |
| **XSLT-фильтр** | Трансформация XML |
| **SSI-фильтр** | Server Side Includes |
| **Преобразование изображений** | Обработка изображений на лету |

### 🔒 Безопасность и протоколы

| Функция | Описание |
|---------|----------|
| **SSL/TLS** | Полная поддержка SSL и TLS SNI |
| **HTTP/2** | Поддержка HTTP/2 с приоритизацией |
| **HTTP/3** | Поддержка нового протокола HTTP/3 |

---

## 🚀 Другие возможности HTTP-сервера

### 🏗️ Архитектура и гибкость

| Возможность | Описание |
|-------------|----------|
| **Виртуальные серверы** | Определение по IP-адресу и имени |
| **Keep-alive** | Поддержка постоянных соединений |
| **Pipelined соединения** | Конвейерная обработка запросов |

### 📊 Логирование

| Возможность | Описание |
|-------------|----------|
| **Форматы логов** | Настраиваемые форматы |
| **Буферизованная запись** | Эффективная запись в лог |
| **Ротация логов** | Быстрая ротация без перезапуска |
| **Syslog** | Запись в системный лог |

### 🎨 Обработка запросов

| Возможность | Описание |
|-------------|----------|
| **Страницы ошибок** | Специальные страницы для 3xx-5xx |
| **Rewrite-модуль** | Изменение URI с помощью regex |
| **Ограничение доступа** | По IP, паролю, подзапросу |
| **HTTP referer** | Проверка источника запроса |
| **Методы HTTP** | PUT, DELETE, MKCOL, COPY, MOVE |

### 📹 Медиа и производительность

| Возможность | Описание |
|-------------|----------|
| **FLV/MP4 стриминг** | Потоковая передача видео |
| **Ограничение скорости** | Контроль скорости отдачи |
| **Ограничение соединений** | Лимиты с одного адреса |
| **Геолокация** | По IP-адресу |
| **A/B-тестирование** | Разделение трафика |
| **Зеркалирование** | Копирование запросов |

### 🐍 Расширяемость

| Возможность | Описание |
|-------------|----------|
| **Встроенный Perl** | Perl-скрипты в конфигурации |
| **njs** | Сценарный язык для расширения |
| **Модульность** | Подключение модулей по необходимости |

---

## 🔄 Цикл обработки HTTP-запроса

```
1. Клиент отправляет HTTP-запрос
   ↓
2. Ядро выбирает фазовый обработчик (по локации)
   ↓
3. Модуль балансировки выбирает вышестоящий сервер
   ↓
4. Фазовый обработчик передает буфер первому фильтру
   ↓
5. Первый фильтр → Второй фильтр → Третий фильтр (и т.д.)
   ↓
6. Итоговый ответ отправляется клиенту
```

---

## 🛠️ Установка и настройка

### 📦 Установка на сервер (Ubuntu/Debian)

```bash
# Установка
apt install nginx

# Вопрос: Do you want to continue? [Y/n] → Y

# Добавление в автозагрузку
systemctl enable nginx

# Проверка
systemctl is-enabled nginx
# Ожидаемый ответ: enabled
```

### 🚀 Запуск и проверка

```bash
# Запуск сервера
service nginx start

# Проверка статуса
service nginx status
# Ожидаем: Active: active (running)
```

### 🐳 Nginx в Docker

#### Установка Docker

```bash
# Установка необходимых пакетов
apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

# Добавление GPG ключа
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Добавление репозитория
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Обновление пакетов
apt update

# Проверка репозитория
apt-cache policy docker-ce

# Установка Docker
apt install docker-ce

# Проверка статуса
systemctl status docker
# Ожидаем: Active: active (running)

systemctl is-enabled docker
# Ожидаем: enabled
```

#### Запуск Nginx в Docker

```bash
# Создание структуры проекта
mkdir -p /home/webuser/myproject/www
mkdir -p /home/webuser/myproject/nginx_logs

# Создание тестовой страницы
echo '<html><body>Hello from NGINX in Docker!</body></html>' > /home/webuser/myproject/www/index.html

# Запуск контейнера
docker run \
  --name nginx_myproject \
  -p 8080:80 \
  -v /home/webuser/myproject/www:/usr/share/nginx/html \
  -v /home/webuser/myproject/nginx_logs:/var/log/nginx \
  -d nginx
```

---

## ⚙️ Основные директивы Nginx

### 🔧 Глобальные настройки

| Директива | Описание |
|-----------|----------|
| `user` | Пользователь, от имени которого работает nginx (обычно www-data) |
| `worker_processes` | Количество процессов сервера (auto = количество ядер) |
| `pid` | Путь к файлу с PID процесса |
| `include` | Подключение дополнительных конфигурационных файлов |
| `events` | Блок для настройки сетевых соединений |
| `worker_connections` | Максимальное количество одновременных соединений |

### 🌐 HTTP-настройки

| Директива | Описание |
|-----------|----------|
| `http` | Блок директив HTTP-сервера |
| `sendfile` | Метод отправки данных (включить: on) |
| `tcp_nopush` | Оптимизация отправки (on) |
| `tcp_nodelay` | Отключение задержек (on) |
| `keepalive_timeout` | Время ожидания keepalive соединения |
| `types_hash_max_size` | Размер хэш-таблиц типов MIME |

### 🔒 SSL/Безопасность

| Директива | Описание |
|-----------|----------|
| `ssl_protocols` | Включает указанные SSL/TLS протоколы |
| `ssl_prefer_server_ciphers` | Серверные шифры предпочтительнее клиентских |

### 📊 Логирование

| Директива | Описание |
|-----------|----------|
| `access_log` | Путь к логу доступа (off = отключить) |
| `error_log` | Путь к логу ошибок |

### 📦 Сжатие

| Директива | Описание |
|-----------|----------|
| `gzip` | Включение/отключение сжатия |

---

## 📝 Пример базовой конфигурации

```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;

    server {
        listen 80;
        server_name example.com;
        root /var/www/html;
        index index.html;
    }
}
```

---

## 🎯 Сценарии использования

| Сценарий | Конфигурация |
|----------|--------------|
| **Статический сайт** | `root /var/www/html; index index.html;` |
| **Reverse Proxy** | `proxy_pass http://backend:8080;` |
| **Балансировка** | `upstream backend { server web1:80; server web2:80; }` |
| **SSL/TLS** | `listen 443 ssl; ssl_certificate /path/to/cert;` |
| **Кэширование** | `proxy_cache_path /path/to/cache;` |
| **Rate Limiting** | `limit_req_zone $binary_remote_addr zone=mylimit:10m rate=5r/s;` |

---

## 🛠️ Полезные команды

```bash
# Проверка конфигурации
nginx -t

# Перезагрузка конфигурации без остановки
nginx -s reload

# Остановка
nginx -s stop

# Плавная остановка
nginx -s quit

# Просмотр логов
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Проверка статуса
systemctl status nginx
```

---

## 📚 Полезные ссылки

| Ресурс | Ссылка |
|--------|--------|
| Официальная документация | [https://nginx.org/ru/docs/](https://nginx.org/ru/docs/) |
| Настройка HTTPS | [https://nginx.org/ru/docs/http/configuring_https_servers.html](https://nginx.org/ru/docs/http/configuring_https_servers.html) |
| Модули | [https://nginx.org/ru/docs/](https://nginx.org/ru/docs/) |
| Docker Hub | [https://hub.docker.com/_/nginx](https://hub.docker.com/_/nginx) |

---

## 💡 Итоговые рекомендации

| Если вам нужно... | Используйте Nginx |
|-------------------|-------------------|
| ✅ Отдавать статику | Отлично |
| ✅ Балансировать нагрузку | Идеально |
| ✅ Раздавать видео | Поддерживает стриминг |
| ✅ Кэшировать ответы | Встроенная поддержка |
| ✅ Настроить HTTPS | Простая настройка |
| ✅ Высокая производительность | Создан для этого |

**Nginx — мощный и производительный веб-сервер, который справляется с огромными нагрузками и предоставляет богатый функционал для любых задач!** 🚀