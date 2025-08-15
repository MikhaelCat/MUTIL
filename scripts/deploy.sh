#!/bin/bash

# Скрипт для деплоя приложения
set -e

echo "Starting deployment..."

# Перейти в директорию проекта
cd /opt/mutil

# Остановить текущие контейнеры
echo "Stopping current containers..."
docker-compose down

# Подтянуть последние изменения из репозитория
echo "Pulling latest changes..."
git pull origin main

# Подтянуть последние образы Docker
echo "Pulling latest Docker images..."
docker-compose pull

# Запустить новые контейнеры
echo "Starting new containers..."
docker-compose up -d

# Удалить неиспользуемые образы
echo "Cleaning up unused images..."
docker image prune -f

echo "Deployment completed successfully!"