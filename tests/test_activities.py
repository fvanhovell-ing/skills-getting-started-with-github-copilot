import pytest


def test_get_activities(client):
    """Test retrieving all activities"""
    # Arrange - no special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Expected number of activities

    # Verify structure of one activity
    assert "Chess Club" in data
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    email = "test@example.com"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]

    # Verify participant was added
    response2 = client.get("/activities")
    activities = response2.json()
    assert email in activities[activity]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    # Arrange
    email = "test@example.com"
    activity = "NonExistent Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up(client):
    """Test signup when student is already signed up"""
    # Arrange
    email = "test@example.com"
    activity = "Chess Club"

    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act - second signup
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" in data["detail"]


def test_signup_activity_full(client):
    """Test signup when activity is at capacity"""
    # Arrange
    activity = "Basketball Team"
    email = "overflow@example.com"

    # Fill the activity to capacity
    response = client.get("/activities")
    initial = response.json()[activity]
    spots_left = initial["max_participants"] - len(initial["participants"])

    for i in range(spots_left):
        client.post(f"/activities/{activity}/signup?email=filler{i}@example.com")

    # Act - try to signup when full
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Activity is full" in data["detail"]


def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    # Arrange
    email = "test@example.com"
    activity = "Chess Club"

    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]

    # Verify participant was removed
    response2 = client.get("/activities")
    activities = response2.json()
    assert email not in activities[activity]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister from non-existent activity"""
    # Arrange
    email = "test@example.com"
    activity = "NonExistent Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_participant_not_found(client):
    """Test unregister when participant is not signed up"""
    # Arrange
    email = "notsignedup@example.com"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]