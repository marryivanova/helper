# 📊 Prometheus - Система мониторинга и сбора метрик

## 🔗 Ресурсы

| Ресурс | Ссылка |
|--------|--------|
| **Официальный сайт** | [https://prometheus.io/](https://prometheus.io/) |
| **Исходный код** | [https://github.com/prometheus/prometheus](https://github.com/prometheus/prometheus) |
| **Пример архитектуры** | `\src\prometheus` |

---

## 🎯 Что такое Prometheus?

**Prometheus** — это программа, которая собирает и хранит **числа (метрики)** с ваших серверов, приложений и сервисов, а потом позволяет смотреть на них в виде графиков.

### 📊 Какие данные собирает?

| Тип метрики | Пример |
|-------------|--------|
| 🌡️ **Системные** | Температура процессора, нагрузка, свободная память |
| 📈 **Бизнес-метрики** | Количество запросов к сайту, активные пользователи |
| ⚠️ **Ошибки** | Количество ошибок в логах, 5xx ответы |
| ⏱️ **Время отклика** | Задержки ответа API, время выполнения запросов |

---

## 🏗️ Архитектура мониторинга и логирования

### Схема взаимодействия

```mermaid
graph LR
    A[Ваше приложение] -->|отдает метрики| B[Prometheus]
    A -->|логи| C[Promtail]
    C -->|отправляет логи| D[Loki]
    B -->|забирает данные| E[Grafana]
    D -->|отдает логи| E
    F[Node Exporter] -->|системные метрики| B
    G[Nginx] -->|проксирует| A
    H[Alertmanager] -->|уведомления| I[Telegram/Slack/Email]
    B -->|алерты| H
```

### Компоненты системы

| Компонент | Роль |
|-----------|------|
| **Server** | Основное приложение, генерирует логи |
| **Nginx** | Reverse Proxy, SSL, маршрутизация |
| **Promtail** | Агент сбора логов, отправляет в Loki |
| **Prometheus** | Сервер сбора метрик (числа) |
| **Node Exporter** | Сбор метрик железа (CPU, RAM, диск) |
| **Grafana** | Визуализация графиков и дашбордов |
| **Loki** | Хранилище логов |
| **Alertmanager** | Отправка уведомлений |

---

## 🔄 Принцип работы

### Pull-модель

```
[Ваше приложение] ---отдает метрики--> [Prometheus] ---забирает данные--> [Grafana (графики)]
       ^                              |
       |                              |
       +---все работает само---------+
```

**Ключевая особенность:** Prometheus сам **ходит (pull)** к приложениям за метриками, а не ждет, пока ему пришлют (push).

### Цикл работы

```
1. Prometheus опрашивает цели каждые N секунд (scrape_interval)
2. Цели отдают метрики в формате, понятном Prometheus
3. Prometheus сохраняет метрики в своей временной базе данных (TSDB)
4. Grafana подключается к Prometheus и строит графики
5. Alertmanager проверяет правила и отправляет уведомления
```

---

## 🧩 Компоненты Prometheus

### 🎯 Targets (Цели)

Это то, что вы мониторите:

| Тип цели | Пример |
|----------|--------|
| **Сервер** | Linux сервер с Node Exporter |
| **База данных** | PostgreSQL, MySQL |
| **Приложение** | Ваш веб-сервер с /metrics |
| **Сервис** | Docker, Kubernetes |

### 📦 Экспортеры

Маленькие программки-переводчики, которые превращают системные показатели в метрики для Prometheus.

| Экспортер | Назначение |
|-----------|------------|
| **Node Exporter** | Системные метрики (CPU, RAM, диск) |
| **MySQL Exporter** | Метрики MySQL |
| **PostgreSQL Exporter** | Метрики PostgreSQL |
| **Nginx Exporter** | Метрики Nginx |
| **Blackbox Exporter** | Проверка доступности (ping, http) |
| **cAdvisor** | Метрики Docker контейнеров |

### 📊 Prometheus (Центральный сервер)

- Собирает метрики со всех экспортеров
- Хранит их в TSDB (Time Series Database)
- Предоставляет API для запросов (PromQL)

### 📈 Grafana

- Web-интерфейс с красивыми дашбордами
- Подключается к Prometheus как источнику данных
- Строит графики из метрик

### 🚨 Alertmanager

Отправляет уведомления, если что-то пошло не так:

```yaml
# Пример правила алерта
groups:
- name: alert.rules
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage > 90
    for: 5m
    annotations:
      summary: "CPU usage is high"
```

---

## 📖 Ключевые понятия (Обязательно к запоминанию)

| Термин | Объяснение | Пример |
|--------|------------|--------|
| **Метрика** | Просто число с именем | `cpu_usage_percent = 42.5` |
| **Лейблы** | Теги для метрики | `cpu_usage_percent{core="1", server="web1"}` |
| **Pull** | Prometheus сам забирает данные | Активный опрос, а не ожидание |
| **Scrape** | Один цикл опроса целей | Раз в 15 секунд |
| **Scrape Interval** | Интервал опроса | `scrape_interval: 15s` |
| **Экспортер** | Переводчик системных данных | Node Exporter, MySQL Exporter |
| **Target** | Цель для мониторинга | `localhost:9100` (Node Exporter) |
| **Alertmanager** | Отправка уведомлений | Telegram, Slack, Email |

---

## ⚙️ Примеры конфигурации

### 📄 federated_client.yml (Prometheus)

```yaml
# Конфигурация Prometheus
global:
  scrape_interval: 15s      # Опрос каждые 15 секунд

scrape_configs:
  - job_name: 'server-node'
    static_configs:
      - targets: ['node-exporter:9100']   # Node Exporter
        labels:
          service: 'webserver'
          environment: 'production'
  
  - job_name: 'application'
    static_configs:
      - targets: ['app:8080/metrics']     # Метрики приложения
        labels:
          service: 'app'
  
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113/metrics']   # Метрики Nginx
```

### 📄 promtail.yml (Promtail)

```yaml
# Конфигурация Promtail для сбора логов
scrape_configs:
  - job_name: 'application-logs'
    static_configs:
      - targets: ['localhost']
        labels:
          job: 'hw_auto'
          service: 'webserver'
        __path__: /var/server/log/server/*.log   # Путь к логам

clients:
  - url: http://ip-vps:port/loki/api/v1/push    # Отправка в Loki
```

### 🐳 Docker Compose пример

```yaml
version: '3'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./promtail.yml:/etc/promtail/promtail.yml
      - /var/log:/var/log
      - logs-data:/var/server/log

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"

volumes:
  prometheus-data:
  grafana-data:
  logs-data:
```

---

## 🛠️ Полезные команды

### Prometheus

```bash
# Запуск Prometheus с кастомной конфигурацией
prometheus --config.file=prometheus.yml --web.enable-lifecycle

# Проверка конфигурации
promtool check config prometheus.yml

# Запрос метрик через API
curl http://localhost:9090/api/v1/query?query=up

# Перезагрузка конфигурации без перезапуска
curl -X POST http://localhost:9090/-/reload
```

### Node Exporter

```bash
# Запуск Node Exporter
node_exporter --web.listen-address=:9100 --collector.diskstats

# Проверка метрик
curl http://localhost:9100/metrics
```

### Grafana

```bash
# Запуск Grafana
grafana-server --config=/etc/grafana/grafana.ini

# Добавление источника данных через API
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{"name":"Prometheus","type":"prometheus","url":"http://prometheus:9090"}'
```

---

## 📊 Популярные дашборды Grafana

| ID | Название | Назначение |
|----|----------|------------|
| **1860** | Node Exporter Full | Полный мониторинг сервера |
| **11074** | Nginx Metrics | Мониторинг Nginx |
| **7362** | Docker Monitoring | Метрики Docker контейнеров |
| **9123** | PostgreSQL | Мониторинг PostgreSQL |
| **10000** | Redis Dashboard | Метрики Redis |

```bash
# Импорт дашборда через API
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d '{"dashboard":{"id":null,"title":"Node Exporter"},"overwrite":true}'
```

---

## 📝 Примеры метрик

### Метрики Node Exporter

```promql
# Нагрузка на CPU
rate(node_cpu_seconds_total{mode="user"}[5m])

# Свободная память
node_memory_MemFree_bytes / node_memory_MemTotal_bytes * 100

# Загрузка диска
rate(node_disk_read_bytes_total[5m]) / 1024 / 1024

# Сетевой трафик
rate(node_network_receive_bytes_total[5m])
```

### Метрики приложения

```promql
# Количество запросов
rate(http_requests_total{status="200"}[5m])

# Время ответа
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Активные соединения
active_connections

# Ошибки
rate(http_requests_total{status=~"5.."}[5m])
```

---

## 🚨 Настройка алертов

### Правила алертов (alert.rules)

```yaml
groups:
  - name: server_alerts
    rules:
      - alert: HighCPUUsage
        expr: (100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value }}%"

      - alert: LowMemory
        expr: (node_memory_MemFree_bytes / node_memory_MemTotal_bytes) * 100 < 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low memory on {{ $labels.instance }}"
          description: "Memory usage is {{ $value }}%"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "Instance {{ $labels.instance }} is not responding"
```

### Конфигурация Alertmanager (alertmanager.yml)

```yaml
route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'telegram'

receivers:
  - name: 'telegram'
    telegram_configs:
      - bot_token: 'YOUR_BOT_TOKEN'
        chat_id: -123456789
        message: |
          {{ range .Alerts }}
          🔔 *{{ .Labels.alertname }}*
          Severity: {{ .Labels.severity }}
          {{ .Annotations.summary }}
          {{ .Annotations.description }}
          {{ end }}
```

---

## 🎯 Сценарии использования

| Сценарий | Решение |
|----------|---------|
| 🔍 **Мониторинг сервера** | Node Exporter + Grafana |
| 📱 **Трекинг приложения** | Собственные метрики + Prometheus |
| 📊 **Аналитика бизнеса** | Метрики запросов, пользователей |
| 🚨 **Alerting** | Alertmanager + Telegram/Slack |
| 📈 **Долгосрочное хранение** | Thanos или VictoriaMetrics |
| 🔄 **Kubernetes** | kube-state-metrics + cAdvisor |
| 🐳 **Docker контейнеры** | cAdvisor + Node Exporter |

---

## 📚 Полезные ссылки

| Ресурс | Ссылка |
|--------|--------|
| Официальная документация | [https://prometheus.io/docs/](https://prometheus.io/docs/) |
| Экспортеры | [https://prometheus.io/docs/instrumenting/exporters/](https://prometheus.io/docs/instrumenting/exporters/) |
| PromQL | [https://prometheus.io/docs/prometheus/latest/querying/basics/](https://prometheus.io/docs/prometheus/latest/querying/basics/) |
| Grafana Dashboards | [https://grafana.com/grafana/dashboards/](https://grafana.com/grafana/dashboards/) |
| Alertmanager | [https://prometheus.io/docs/alerting/latest/alertmanager/](https://prometheus.io/docs/alerting/latest/alertmanager/) |

---

## 💡 Итоговые рекомендации

| Если вам нужно... | Используйте |
|-------------------|-------------|
| ✅ Собирать системные метрики | Node Exporter + Prometheus |
| ✅ Собирать логи | Promtail + Loki |
| ✅ Строить графики | Grafana + Prometheus |
| ✅ Отправлять алерты | Alertmanager + Telegram/Slack |
| ✅ Мониторить Docker | cAdvisor + Node Exporter |
| ✅ Мониторить Kubernetes | kube-state-metrics |

**Prometheus — мощная система мониторинга, которая вместе с Grafana, Loki и Alertmanager образует полный стек для наблюдения за вашей инфраструктурой!** 🚀