from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.consts import TaskPriority
from tests.conftest import fake


def test_create_task(client: TestClient) -> None:
    data = {"name": fake.name(), "description": fake.text(), "priority": TaskPriority.MEDIUM}

    response = client.post(f"{settings.API_V1_STR}/tasks", json=data)

    assert response.status_code == 201
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["priority"] == data["priority"]
    assert "id" in content


def test_get_tasks(client: TestClient) -> None:
    created_tasks = []
    for _ in range(3):
        data = {"name": fake.name(), "description": fake.text(), "priority": TaskPriority.MEDIUM}
        response = client.post(f"{settings.API_V1_STR}/tasks", json=data)
        assert response.status_code == 201
        content = response.json()
        created_tasks.append(content["id"])

    response = client.get(f"{settings.API_V1_STR}/tasks")

    assert response.status_code == 200
    content = response.json()
    ids = [task["id"] for task in content]
    for id in created_tasks:
        assert id in ids


def test_get_task(client: TestClient) -> None:
    data = {"name": fake.name(), "description": fake.text(), "priority": TaskPriority.LOW}
    response = client.post(f"{settings.API_V1_STR}/tasks", json=data)
    assert response.status_code == 201
    content = response.json()
    created_task = content["id"]

    response = client.get(f"{settings.API_V1_STR}/tasks/{created_task}")

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["priority"] == data["priority"]
    assert content["id"] == created_task


def test_delete_task(client: TestClient) -> None:
    data = {"name": fake.name(), "description": fake.text(), "priority": TaskPriority.LOW}
    response = client.post(f"{settings.API_V1_STR}/tasks", json=data)
    assert response.status_code == 201
    content = response.json()
    created_task = content["id"]

    response = client.delete(f"{settings.API_V1_STR}/tasks/{created_task}")

    assert response.status_code == 204


def test_check_task_status(client: TestClient) -> None:
    data = {"name": fake.name(), "description": fake.text(), "priority": TaskPriority.LOW}
    response = client.post(f"{settings.API_V1_STR}/tasks", json=data)
    assert response.status_code == 201
    content = response.json()
    created_task = content["id"]

    response = client.delete(f"{settings.API_V1_STR}/tasks/{created_task}")

    assert response.status_code == 204
