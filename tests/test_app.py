import pytest
from fastapi.testclient import TestClient

import src.app as app_module


CHESS_CLUB_PATH = "/activities/Chess%20Club"


@pytest.fixture
def activity_data(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["existing@example.com"],
        },
        "Basketball Team": {
            "description": "Play basketball",
            "schedule": "Mondays",
            "max_participants": 10,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client, activity_data):
    # Arrange
    expected_activities = activity_data

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activity_data):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(f"{CHESS_CLUB_PATH}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activity_data["Chess Club"]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client, activity_data):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.post(f"{CHESS_CLUB_PATH}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activity_data["Chess Club"]["participants"] == [email]


def test_remove_participant_removes_registration(client, activity_data):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        f"{CHESS_CLUB_PATH}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activity_data["Chess Club"]["participants"]
    activities_response = client.get("/activities")
    assert activities_response.json()["Chess Club"]["participants"] == []


def test_remove_participant_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_not_found_for_unregistered_participant(client):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete(
        f"{CHESS_CLUB_PATH}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}