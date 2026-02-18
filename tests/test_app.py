"""Test suite for the Mergington High School Activities API"""
import pytest


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities(self, client):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check that activities have required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activities_have_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # At least some activities should have participants
        has_participants = any(
            len(activity["participants"]) > 0 
            for activity in activities.values()
        )
        assert has_participants


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=test@example.com"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "test@example.com" in result["message"]
        assert "Basketball" in result["message"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_duplicate_signup(self, client):
        """Test that duplicate signups are prevented"""
        email = "duplicate@example.com"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Tennis Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(f"/activities/Tennis Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_adds_to_participants_list(self, client):
        """Test that signup adds email to participants list"""
        email = "newparticipant@example.com"
        activity = "Art Studio"
        
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Sign up
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify participant was added
        response3 = client.get("/activities")
        new_count = len(response3.json()[activity]["participants"])
        assert new_count == initial_count + 1
        assert email in response3.json()[activity]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successful unregistration from an activity"""
        email = "tounregister@example.com"
        activity = "Chess Club"
        
        # First signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "Unregistered" in result["message"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistent/unregister?email=test@example.com"
        )
        assert response.status_code == 404
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistering when not signed up"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_removes_from_participants(self, client):
        """Test that unregister removes email from participants list"""
        email = "removetest@example.com"
        activity = "Science Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify added
        response1 = client.get("/activities")
        assert email in response1.json()[activity]["participants"]
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify removed
        response3 = client.get("/activities")
        assert email not in response3.json()[activity]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]
