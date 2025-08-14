import pytest
from fastapi.testclient import TestClient
from app.main import fastapi_app
from app.services.task_service import generate_random_task

client = TestClient(fastapi_app)

def test_generate_random_task():
    """Тест генерации случайного задания."""
    task = generate_random_task()
    assert isinstance(task, str)
    assert len(task) > 0

def test_create_task():
    """Тест создания задания через API."""
    response = client.post(
        "/api/tasks/",
        json={"text": "Тестовое задание"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Тестовое задание"
    assert "id" in data

def test_read_task():
    """Тест получения задания по ID."""
    # Сначала создаем задание
    create_response = client.post(
        "/api/tasks/",
        json={"text": "Тестовое задание для чтения"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Затем получаем его
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Тестовое задание для чтения"
    assert data["id"] == task_id

def test_read_nonexistent_task():
    """Тест получения несуществующего задания."""
    response = client.get("/api/tasks/999999")
    assert response.status_code == 404