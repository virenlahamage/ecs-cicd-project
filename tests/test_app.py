import os

os.environ["APP_VERSION"] = "1.0.0"
os.environ["GIT_COMMIT"] = "test-commit"
os.environ["APP_ENV"] = "test"

from app.app import app


def test_home_page():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"ECS CI/CD Demo Application" in response.data
    assert b"1.0.0" in response.data


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_version_endpoint():
    client = app.test_client()
    response = client.get("/version")

    assert response.status_code == 200
    data = response.get_json()

    assert data["version"] == "1.0.0"
    assert data["commit"] == "test-commit"
    assert data["environment"] == "test"
