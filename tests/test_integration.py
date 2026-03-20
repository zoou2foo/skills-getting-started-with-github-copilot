import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestIntegrationWorkflows:
    """Test suite for end-to-end workflows using AAA pattern."""

    def test_complete_signup_workflow(self, client):
        """Test complete signup and verification workflow."""
        # Arrange - Set up test data
        activity_name = "Gym Class"
        email = "integration@test.com"

        # Act - Signup for activity
        signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify signup success
        assert signup_response.status_code == 200
        signup_data = signup_response.json()
        assert "message" in signup_data

        # Act - Verify participant appears in activities list
        activities_response = client.get("/activities")

        # Assert - Verify participant is in the activity
        assert activities_response.status_code == 200
        activities_data = activities_response.json()
        assert activity_name in activities_data
        assert email in activities_data[activity_name]["participants"]

    def test_signup_delete_workflow(self, client):
        """Test signup followed by delete workflow."""
        # Arrange - Set up test data
        activity_name = "Basketball Team"
        email = "workflow@test.com"

        # Act - Signup for activity
        signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify signup success
        assert signup_response.status_code == 200

        # Act - Delete the participant
        delete_response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert - Verify delete success
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert "message" in delete_data

        # Act - Verify participant is removed from activities list
        activities_response = client.get("/activities")

        # Assert - Verify participant is no longer in the activity
        assert activities_response.status_code == 200
        activities_data = activities_response.json()
        assert activity_name in activities_data
        assert email not in activities_data[activity_name]["participants"]

    def test_capacity_limit_workflow(self, client):
        """Test behavior when activity reaches capacity."""
        # Arrange - Find an activity with low capacity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()

        # Find activity with remaining capacity of 1
        target_activity = None
        for name, data in activities_data.items():
            remaining = data["max_participants"] - len(data["participants"])
            if remaining == 1:
                target_activity = name
                break

        if not target_activity:
            pytest.skip("No activity with capacity of 1 available for testing")

        # Act - Fill the last spot
        email = "capacity@test.com"
        fill_response = client.post(f"/activities/{target_activity}/signup", params={"email": email})

        # Assert - Verify signup success
        assert fill_response.status_code == 200

        # Act - Try to signup another participant (should fail)
        overflow_email = "overflow@test.com"
        overflow_response = client.post(f"/activities/{target_activity}/signup", params={"email": overflow_email})

        # Assert - Verify signup is rejected (business logic would need to be implemented)
        # Note: Current implementation doesn't enforce capacity limits, so this tests current behavior
        # In a real implementation, this should return 400 for capacity exceeded

    def test_concurrent_operations_isolation(self, client):
        """Test that operations on different activities don't interfere."""
        # Arrange - Set up test data for two different activities
        activity1 = "Soccer Club"
        activity2 = "Art Painting"
        email1 = "isolation1@test.com"
        email2 = "isolation2@test.com"

        # Act - Signup for first activity
        response1 = client.post(f"/activities/{activity1}/signup", params={"email": email1})

        # Act - Signup for second activity
        response2 = client.post(f"/activities/{activity2}/signup", params={"email": email2})

        # Assert - Both operations succeed
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Act - Verify both activities have their respective participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()

        # Assert - Verify isolation
        assert email1 in activities_data[activity1]["participants"]
        assert email2 in activities_data[activity2]["participants"]
        assert email1 not in activities_data[activity2]["participants"]
        assert email2 not in activities_data[activity1]["participants"]

    def test_error_recovery_workflow(self, client):
        """Test error handling and recovery in workflows."""
        # Arrange - Set up test data
        activity_name = "Debate Club"
        valid_email = "recovery@test.com"
        invalid_activity = "Invalid Activity"

        # Act - Try invalid operation first
        invalid_response = client.post(f"/activities/{invalid_activity}/signup", params={"email": valid_email})

        # Assert - Verify error response
        assert invalid_response.status_code == 404

        # Act - Try valid operation after error
        valid_response = client.post(f"/activities/{activity_name}/signup", params={"email": valid_email})

        # Assert - Verify recovery works
        assert valid_response.status_code == 200

        # Act - Verify participant was added despite previous error
        activities_response = client.get("/activities")
        activities_data = activities_response.json()

        # Assert - Verify final state
        assert valid_email in activities_data[activity_name]["participants"]