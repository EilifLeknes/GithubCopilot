from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

baseline_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(baseline_activities))
    yield
    activities.clear()
    activities.update(deepcopy(baseline_activities))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_available_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_new_participant(client):
    email = "teststudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    email = "duplicate@mergington.edu"
    first_response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unregisters_student(client):
    email = "michael@mergington.edu"
    assert email in activities["Chess Club"]["participants"]

    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]
