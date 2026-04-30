import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset the in-memory activities before each test
    for activity in activities.values():
        if 'participants' in activity:
            if isinstance(activity['participants'], list):
                activity['participants'].clear()
    # Add initial participants for specific activities
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]


def test_get_activities():
    # Arrange done by fixture
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    # Act
    response = client.post("/activities/Art Club/signup?email=" + email)
    # Assert
    assert response.status_code == 200
    assert email in activities["Art Club"]["participants"]


def test_signup_duplicate():
    # Arrange
    email = "emma@mergington.edu"
    # Act
    response = client.post(f"/activities/Programming Class/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/Nonexistent/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success():
    # Arrange
    email = "emma@mergington.edu"
    # Act
    response = client.delete(f"/activities/Programming Class/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities["Programming Class"]["participants"]


def test_unregister_not_found():
    # Arrange
    email = "notfound@mergington.edu"
    # Act
    response = client.delete(f"/activities/Art Club/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    # Act
    response = client.delete(f"/activities/Nonexistent/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
