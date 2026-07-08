# 🔐 Всё о Keycloak: зачем нужен, кому подходит и какие преимущества даёт

## 📌 Введение

**Keycloak** — это решение для аутентификации и авторизации, которое также берёт на себя управление пользователями и безопасность в широком смысле.

> Безопасность — это всегда сложно и больно, а Keycloak берёт эту историю на себя.

### 🔗 Пример использования

```
\helper\src\bridge
```

---

Статьи:
- В целом о KK: https://habr.com/ru/companies/X5Tech/articles/486778/
- Как развернуть: https://timeweb.cloud/tutorials/servers/nastrojka-keycloak


## ✅ Основные преимущества

| Преимущество | Описание |
|--------------|----------|
| 🚀 **Низкий порог входа** | Проще в освоении по сравнению с Hydra |
| 🔄 **SSO (Single Sign-On)** | Бесшовный переход между приложениями |
| 💰 **Бесплатный** | Open Source решение |
| 🛠️ **Богатый функционал** | Готовые решения для большинства задач |
| 📚 **Хорошая документация** | Большое сообщество и примеры |

---

## 📖 Основные понятия

Прежде чем разбираться с решениями, важно определить термины:

| Термин | Определение |
|--------|-------------|
| 🆔 **Идентификация** | Процедура распознавания субъекта по его идентификатору (имя, логин, номер) |
| 🔑 **Аутентификация** | Проверка подлинности (пароль, электронная подпись и т.д.) |
| 🔓 **Авторизация** | Предоставление доступа к ресурсу (например, к электронной почте) |

### Процесс аутентификации и авторизации

```
Пользователь → Идентификация → Аутентификация → Авторизация → Доступ
```

---

## 🎯 Базовый функционал Keycloak

### 🚀 Основные возможности

| Функционал | Описание |
|------------|----------|
| **SSO & SLO** | Single-Sign On и Single-Sign Out для браузерных приложений |
| **Протоколы** | Поддержка OpenID Connect, OAuth 2.0, SAML |
| **Identity Brokering** | Аутентификация через внешних провайдеров (OpenID Connect/SAML) |
| **Social Login** | Интеграция с Google, GitHub, Facebook, Twitter |
| **User Federation** | Синхронизация из LDAP, Active Directory и других источников |
| **Kerberos Bridge** | Автоматическая аутентификация через Kerberos |

### 🛠️ Управление и настройка

| Возможность | Описание |
|-------------|----------|
| **Admin Console** | Web-интерфейс для управления настройками |
| **Account Management** | Самостоятельное управление профилем пользователей |
| **Кастомизация** | Настройка под фирменный стиль компании |
| **2FA Authentication** | TOTP/HOTP с Google Authenticator или FreeOTP |
| **Login Flows** | Саморегистрация, восстановление пароля и другие сценарии |

### 📊 Расширенные возможности

| Возможность | Описание |
|-------------|----------|
| **Session Management** | Централизованное управление сессиями |
| **Token Mappers** | Привязка атрибутов, ролей и данных в токены |
| **Гибкое управление** | Политики через realm, application и пользователей |
| **CORS Support** | Встроенная поддержка CORS в клиентских адаптерах |
| **SPI (Service Provider Interfaces)** | Расширение функционала через плагины |

### 🔌 Клиентские адаптеры

Keycloak поддерживает готовые адаптеры для:

| Платформа/Фреймворк |
|---------------------|
| JavaScript-приложения |
| WildFly / JBoss EAP |
| Apache Fuse |
| Apache Tomcat |
| Jetty |
| Spring Framework |
| OpenID Connect Relying Party Library |
| SAML 2.0 Service Provider Library |

---

## 🔧 REST API

Keycloak предоставляет полноценный REST API для управления всеми аспектами:

```
https://www.keycloak.org/docs-api/8.0/rest-api/index.html
```

### Примеры использования API

```bash
# Получение токена
curl -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password"

# Создание пользователя
curl -X POST http://localhost:8080/admin/realms/my-realm/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "enabled": true
  }'
```

---

## 🚀 Быстрый старт

### Установка через Docker

```bash
# Запуск Keycloak
docker run -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest \
  start-dev
```

### Создание Realm

```bash
# Создание нового Realm через REST API
curl -X POST http://localhost:8080/admin/realms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "realm": "my-app",
    "enabled": true,
    "displayName": "My Application"
  }'
```

---

## 🎯 Когда использовать Keycloak

| Сценарий | Почему Keycloak |
|----------|-----------------|
| 🏢 **Корпоративные приложения** | Единый вход, управление пользователями |
| 🌐 **Микросервисная архитектура** | Централизованная аутентификация и авторизация |
| 🔐 **Высокие требования к безопасности** | Готовые решения для 2FA, SSO, управления сессиями |
| 📱 **Мобильные и веб-приложения** | Поддержка OAuth 2.0 и OpenID Connect |
| 👥 **Разные типы пользователей** | Роли, группы, гибкие политики доступа |

---

## 📚 Полезные ссылки

| Ресурс | Ссылка |
|--------|--------|
| Официальный сайт | [https://www.keycloak.org/](https://www.keycloak.org/) |
| Документация | [https://www.keycloak.org/documentation](https://www.keycloak.org/documentation) |
| REST API | [https://www.keycloak.org/docs-api/](https://www.keycloak.org/docs-api/) |
| GitHub | [https://github.com/keycloak/keycloak](https://github.com/keycloak/keycloak) |

---

## 💡 Итоговые рекомендации

| Если вам нужно... | Keycloak подходит |
|-------------------|-------------------|
| ✅ SSO для нескольких приложений | ✔️ Идеально |
| ✅ Социальный вход (Google, GitHub) | ✔️ Отлично |
| ✅ Гибкое управление пользователями | ✔️ Хорошо |
| ✅ 2FA и безопасность | ✔️ Отлично |
| ✅ Микросервисы и API безопасность | ✔️ Идеально |
| ❌ Простой микросервис без пользователей | Возможно, избыточно |

**Keycloak — мощный и гибкий инструмент для управления идентификацией, который значительно упрощает реализацию безопасности в ваших приложениях.** 🚀