# 🎨 MUTIL - Генератор безумных творческих заданий

## Сервис для генерации абсурдных творческих заданий с веб-интерфейсом, Telegram-ботом и системой голосования за лучшие ответы.

## 🌟 Особенности
* 🎲 Случайные задания ("напиши письмо холодильнику", "сфотографируй тень в стиле нуар")

* 👍 Голосование за лучшие креативные ответы

* 🤖 Telegram-бот для получения заданий

* 🧠 Интеграция с ChatGPT или локальными LLM

* 🖼️ Галерея самых безумных работ пользователей

## 🛠 Технологический стек
## Backend:

* Python 3.11

* FastAPI (основное API)

* Flask (веб-интерфейс)

* SQLAlchemy (PostgreSQL)

* Redis (кеширование)

## Frontend:

* HTML5

* CSS3 

* JavaScript 

## Инфраструктура:

* Docker + Docker Compose

* GitLab CI/CD

* PostgreSQL

* Redis

## 🚀 Быстрый старт
### Требования

* Docker 20.10+

* Docker Compose 2.0+

* Python 3.11+ 

### Запуск через Docker
# 1. Клонировать репозиторий
     git clone https://gitlab.com/yourusername/mutil.git

  
     cd mutil

# 2. Создать файл .env (на основе .env.example)
    cp .env.example .env
# Заполнить реальными значениями (OPENAI_API_KEY и др.)

# 3. Запустить сервисы
    docker-compose -f docker/docker-compose.yml up --build

# 4. Открыть в браузере:
# Веб-интерфейс:   
    http://localhost:5000
# API документация: 
    http://localhost:8000/api/docs
## 🤖 Telegram-бот
### Бот доступен по адресу @MutilBot 

### Команды:

* /random - получить случайное задание

* /top - топ лучших работ

* /help - справка
