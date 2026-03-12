import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities_returns_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in app_module.activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_removes_participant():
    email = "james@mergington.edu"
    activity_name = "Basketball Team"

    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 200
    assert email not in app_module.activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_missing_participant_returns_404():
    email = "notregistered@mergington.edu"
    activity_name = "Basketball Team"

    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up"
