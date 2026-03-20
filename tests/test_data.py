import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestDataValidation:
    """Test suite for data validation and business logic using AAA pattern."""

    def test_activity_data_structure_integrity(self, client, sample_activity_data):
        """Test that activity data maintains proper structure."""
        # Arrange - Get current activities data
        response = client.get("/activities")
        activities = response.json()

        # Act - Validate each activity structure
        for activity_name, activity_data in activities.items():
            # Assert - Verify required fields exist
            assert "description" in activity_data, f"Activity {activity_name} missing description"
            assert "schedule" in activity_data, f"Activity {activity_name} missing schedule"
            assert "max_participants" in activity_data, f"Activity {activity_name} missing max_participants"
            assert "participants" in activity_data, f"Activity {activity_name} missing participants"

            # Assert - Verify data types
            assert isinstance(activity_data["description"], str), f"Description should be string for {activity_name}"
            assert isinstance(activity_data["schedule"], str), f"Schedule should be string for {activity_name}"
            assert isinstance(activity_data["max_participants"], int), f"Max participants should be int for {activity_name}"
            assert isinstance(activity_data["participants"], list), f"Participants should be list for {activity_name}"

            # Assert - Verify max_participants is reasonable
            assert activity_data["max_participants"] > 0, f"Max participants should be positive for {activity_name}"
            assert activity_data["max_participants"] <= 50, f"Max participants should not exceed 50 for {activity_name}"

    def test_participant_email_format_validation(self, client):
        """Test that participant emails follow expected format."""
        # Arrange - Get activities with participants
        response = client.get("/activities")
        activities = response.json()

        # Act - Check each participant's email format
        for activity_name, activity_data in activities.items():
            for email in activity_data["participants"]:
                # Assert - Basic email format validation
                assert "@" in email, f"Invalid email format: {email} in {activity_name}"
                assert "." in email, f"Invalid email format: {email} in {activity_name}"
                assert len(email) > 5, f"Email too short: {email} in {activity_name}"
                assert " " not in email, f"Email contains spaces: {email} in {activity_name}"

    def test_participant_uniqueness_within_activity(self, client):
        """Test that participants are unique within each activity."""
        # Arrange - Get activities data
        response = client.get("/activities")
        activities = response.json()

        # Act - Check uniqueness for each activity
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]

            # Assert - No duplicates within activity
            assert len(participants) == len(set(participants)), f"Duplicate participants in {activity_name}: {participants}"

    def test_capacity_constraints_logical(self, client):
        """Test that capacity constraints are logically consistent."""
        # Arrange - Get activities data
        response = client.get("/activities")
        activities = response.json()

        # Act - Validate capacity logic for each activity
        for activity_name, activity_data in activities.items():
            current_count = len(activity_data["participants"])
            max_capacity = activity_data["max_participants"]

            # Assert - Current participants don't exceed max capacity
            assert current_count <= max_capacity, f"Activity {activity_name} over capacity: {current_count}/{max_capacity}"

            # Assert - Capacity is reasonable (not zero, not excessively high)
            assert max_capacity >= 1, f"Activity {activity_name} has invalid capacity: {max_capacity}"
            assert max_capacity <= 100, f"Activity {activity_name} has unreasonably high capacity: {max_capacity}"

    def test_activity_name_consistency(self, client):
        """Test that activity names are consistent and valid."""
        # Arrange - Get activities data
        response = client.get("/activities")
        activities = response.json()

        # Act - Validate activity names
        for activity_name in activities.keys():
            # Assert - Activity name is not empty
            assert activity_name.strip(), f"Activity name cannot be empty: '{activity_name}'"

            # Assert - Activity name doesn't contain invalid characters
            invalid_chars = ['<', '>', '&', '"', "'"]
            for char in invalid_chars:
                assert char not in activity_name, f"Activity name contains invalid character '{char}': {activity_name}"

            # Assert - Activity name is reasonable length
            assert 3 <= len(activity_name) <= 50, f"Activity name length invalid: '{activity_name}' (length: {len(activity_name)})"

    def test_schedule_format_consistency(self, client):
        """Test that schedule formats are consistent."""
        # Arrange - Get activities data
        response = client.get("/activities")
        activities = response.json()

        # Act - Validate schedule formats
        for activity_name, activity_data in activities.items():
            schedule = activity_data["schedule"]

            # Assert - Schedule is not empty
            assert schedule.strip(), f"Schedule cannot be empty for {activity_name}"

            # Assert - Schedule contains time-related keywords
            time_keywords = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                           'am', 'pm', ':', 'morning', 'afternoon', 'evening']
            has_time_reference = any(keyword.lower() in schedule.lower() for keyword in time_keywords)
            assert has_time_reference, f"Schedule lacks time reference for {activity_name}: '{schedule}'"