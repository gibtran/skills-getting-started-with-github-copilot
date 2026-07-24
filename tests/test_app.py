import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_data(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"


def test_signup_duplicate_email_returns_error(client):
    # Arrange
    activity = "Chess Club"
    email = "duplicate@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_participant_removes_user(client):
    # Arrange
    activity = "Chess Club"
    email = "remove@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"


def test_unregister_unknown_participant_returns_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "does-not-exist@example.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_when_activity_is_full_returns_error(client):
    # Arrange
    activity = "Tennis Club"
    for index in range(9):
        email = f"full{index}@example.com"
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

    # Act
    response = client.post(f"/activities/{activity}/signup?email=overflow@example.com")

    # Assert
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()
