#!/bin/bash

# Скрипт для проверки здоровья сервисов
set -e

echo "Checking service health..."

# Проверить backend
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is unhealthy"
    exit 1
fi

# Проверить frontend
if curl -f http://localhost:5000/ > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is unhealthy"
    exit 1
fi

echo "All services are healthy!"