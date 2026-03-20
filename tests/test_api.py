import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestActivitiesAPI:
    """Test suite for activities API endpoints using AAA pattern."""

    def test_get_activities_success(self, client):
        """Test successful retrieval of all activities."""
        # Arrange - No special setup needed for this test

        # Act - Make GET request to activities endpoint
        response = client.get("/activities")

        # Assert - Verify response structure and status
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have activities

        # Verify structure of first activity
        first_activity = next(iter(data.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        # Arrange - Set up test data
        activity_name = "Chess Club"
        email = "test@example.com"

        # Act - Make POST request to signup endpoint
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify successful signup
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_for_activity_duplicate(self, client):
        """Test signup with already registered email."""
        # Arrange - Set up test data with existing participant
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act - Attempt to signup again
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify duplicate rejection
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_for_activity_not_found(self, client):
        """Test signup for non-existent activity."""
        # Arrange - Set up test data
        activity_name = "NonExistent Activity"
        email = "test@example.com"

        # Act - Attempt to signup for non-existent activity
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_delete_participant_success(self, client):
        """Test successful removal of a participant."""
        # Arrange - Set up test data
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in Programming Class

        # Act - Make DELETE request to remove participant
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify successful removal
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]

    def test_delete_participant_not_found(self, client):
        """Test removal of non-existent participant."""
        # Arrange - Set up test data
        activity_name = "Chess Club"
        email = "nonexistent@example.com"

        # Act - Attempt to remove non-existent participant
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify 400 response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()

    def test_delete_participant_activity_not_found(self, client):
        """Test removal from non-existent activity."""
        # Arrange - Set up test data
        activity_name = "NonExistent Activity"
        email = "test@example.com"

        # Act - Attempt to remove from non-existent activity
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()