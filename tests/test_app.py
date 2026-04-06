import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)

# Fixture to reset activities before each test
@pytest.fixture(autouse=True)
def reset_activities():
    # Save initial state
    initial_activities = copy.deepcopy(activities)
    yield
    # Reset after test
    activities.clear()
    activities.update(initial_activities)

def test_get_activities():
    # Arrange: No special setup needed
    
    # Act: Call the endpoint
    response = client.get("/activities")
    
    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Arrange: Choose an activity and new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act: Sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check success and data update
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    
    # Verify added to participants
    get_response = client.get("/activities")
    data = get_response.json()
    assert email in data[activity_name]["participants"]

def test_signup_duplicate():
    # Arrange: Sign up once first
    activity_name = "Chess Club"
    email = "dupe@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Should fail with 400
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_invalid_activity():
    # Arrange: Use non-existent activity
    activity_name = "NonExistent"
    email = "test@mergington.edu"
    
    # Act: Try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Should fail with 404
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_remove_success():
    # Arrange: Sign up first
    activity_name = "Programming Class"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act: Remove the participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Check success and data update
    assert response.status_code == 200
    result = response.json()
    assert "Removed" in result["message"]
    
    # Verify removed from participants
    get_response = client.get("/activities")
    data = get_response.json()
    assert email not in data[activity_name]["participants"]

def test_remove_not_signed_up():
    # Arrange: Try to remove someone not signed up
    activity_name = "Gym Class"
    email = "notsigned@mergington.edu"
    
    # Act: Try to remove
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Should fail with 400
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]

def test_remove_invalid_activity():
    # Arrange: Use non-existent activity
    activity_name = "InvalidActivity"
    email = "test@mergington.edu"
    
    # Act: Try to remove
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Should fail with 404
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]