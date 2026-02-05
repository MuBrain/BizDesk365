"""
Power Platform Governance API Tests
Tests for all Power Platform endpoints including:
- Program management
- KPIs
- Workshops CRUD
- Actions CRUD
- Decisions CRUD
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Test authentication flow"""
    
    def test_login_success(self):
        """Test login with demo credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@bizdesk365.local",
            "password": "demo"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["email"] == "demo@bizdesk365.local"
        return data["access_token"]


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "demo@bizdesk365.local",
        "password": "demo"
    })
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.text}")
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestPowerPlatformProgram:
    """Test Power Platform program endpoints"""
    
    def test_get_program(self, auth_headers):
        """GET /api/power-platform/program - Get or create program"""
        response = requests.get(f"{BASE_URL}/api/power-platform/program", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "id" in data, "Program should have an id"
        assert "tenant_id" in data, "Program should have tenant_id"
        assert "status" in data, "Program should have status"
    
    def test_get_kpis(self, auth_headers):
        """GET /api/power-platform/kpis - Get KPIs"""
        response = requests.get(f"{BASE_URL}/api/power-platform/kpis", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        # Verify KPI fields exist
        assert "workshops_completed" in data
        assert "workshop_completion_pct" in data
        assert "items_total" in data
        assert "items_done" in data
        assert "items_validated" in data
        assert "actions_open_count" in data
        assert "decisions_count" in data


class TestPowerPlatformWorkshops:
    """Test Power Platform workshops endpoints"""
    
    def test_get_workshops_list(self, auth_headers):
        """GET /api/power-platform/workshops - Get all workshops"""
        response = requests.get(f"{BASE_URL}/api/power-platform/workshops", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Should return a list"
        assert len(data) == 10, f"Should have 10 workshops, got {len(data)}"
        
        # Verify first workshop structure
        ws = data[0]
        assert "workshop_number" in ws
        assert "title" in ws
        assert "status" in ws
        assert "items_total" in ws
        assert "items_done" in ws
    
    def test_get_workshop_detail(self, auth_headers):
        """GET /api/power-platform/workshops/1 - Get workshop detail"""
        response = requests.get(f"{BASE_URL}/api/power-platform/workshops/1", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["workshop_number"] == 1
        assert "title" in data
        assert "description" in data
        assert "completion_criteria" in data
        assert "items" in data
        assert isinstance(data["items"], list)
    
    def test_get_workshop_not_found(self, auth_headers):
        """GET /api/power-platform/workshops/999 - Workshop not found"""
        response = requests.get(f"{BASE_URL}/api/power-platform/workshops/999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_workshop_status(self, auth_headers):
        """PATCH /api/power-platform/workshops/1 - Update workshop status"""
        # First get current status
        get_response = requests.get(f"{BASE_URL}/api/power-platform/workshops/1", headers=auth_headers)
        original_status = get_response.json()["status"]
        
        # Update to in_progress
        response = requests.patch(
            f"{BASE_URL}/api/power-platform/workshops/1",
            headers=auth_headers,
            json={"status": "in_progress"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["status"] == "in_progress"
        
        # Verify persistence
        verify_response = requests.get(f"{BASE_URL}/api/power-platform/workshops/1", headers=auth_headers)
        assert verify_response.json()["status"] == "in_progress"
    
    def test_update_workshop_completion_criteria(self, auth_headers):
        """PATCH /api/power-platform/workshops/1 - Update completion criteria state"""
        # Get workshop to know criteria
        get_response = requests.get(f"{BASE_URL}/api/power-platform/workshops/1", headers=auth_headers)
        ws_data = get_response.json()
        criteria = ws_data.get("completion_criteria", [])
        
        if criteria:
            # Update first criterion to checked
            new_state = {criteria[0]: True}
            response = requests.patch(
                f"{BASE_URL}/api/power-platform/workshops/1",
                headers=auth_headers,
                json={"completion_criteria_state": new_state}
            )
            assert response.status_code == 200, f"Failed: {response.text}"
            
            # Verify persistence
            verify_response = requests.get(f"{BASE_URL}/api/power-platform/workshops/1", headers=auth_headers)
            verify_data = verify_response.json()
            assert verify_data["completion_criteria_state"].get(criteria[0]) == True


class TestPowerPlatformItems:
    """Test Power Platform items endpoints"""
    
    def test_get_items_list(self, auth_headers):
        """GET /api/power-platform/items - Get all items"""
        response = requests.get(f"{BASE_URL}/api/power-platform/items", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have items"
        
        # Verify item structure
        item = data[0]
        assert "item_id" in item
        assert "workshop_number" in item
        assert "status" in item
    
    def test_get_items_filtered_by_workshop(self, auth_headers):
        """GET /api/power-platform/items?workshop_number=1 - Filter by workshop"""
        response = requests.get(f"{BASE_URL}/api/power-platform/items?workshop_number=1", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        for item in data:
            assert item["workshop_number"] == 1
    
    def test_get_item_detail(self, auth_headers):
        """GET /api/power-platform/items/A1-01 - Get item detail"""
        response = requests.get(f"{BASE_URL}/api/power-platform/items/A1-01", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["item_id"] == "A1-01"
        assert "title" in data
        assert "module_name" in data
    
    def test_update_item(self, auth_headers):
        """PATCH /api/power-platform/items/A1-01 - Update item"""
        response = requests.patch(
            f"{BASE_URL}/api/power-platform/items/A1-01",
            headers=auth_headers,
            json={
                "status": "in_progress",
                "owner_user_id": "TEST_user",
                "notes_markdown": "TEST notes"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["owner_user_id"] == "TEST_user"
        
        # Verify persistence
        verify_response = requests.get(f"{BASE_URL}/api/power-platform/items/A1-01", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data["status"] == "in_progress"


class TestPowerPlatformActions:
    """Test Power Platform actions CRUD"""
    
    created_action_id = None
    
    def test_get_actions_list(self, auth_headers):
        """GET /api/power-platform/actions - Get all actions"""
        response = requests.get(f"{BASE_URL}/api/power-platform/actions", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_action(self, auth_headers):
        """POST /api/power-platform/actions - Create new action"""
        response = requests.post(
            f"{BASE_URL}/api/power-platform/actions",
            headers=auth_headers,
            json={
                "title": "TEST_Action_Title",
                "description": "TEST action description",
                "priority": "high",
                "workshop_number": 1,
                "owner_user_id": "TEST_owner",
                "due_date": "2026-02-15"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["title"] == "TEST_Action_Title"
        assert data["priority"] == "high"
        assert data["status"] == "open"
        assert "id" in data
        
        # Store for later tests
        TestPowerPlatformActions.created_action_id = data["id"]
        
        # Verify persistence via GET
        verify_response = requests.get(f"{BASE_URL}/api/power-platform/actions", headers=auth_headers)
        actions = verify_response.json()
        found = any(a["id"] == data["id"] for a in actions)
        assert found, "Created action not found in list"
    
    def test_update_action(self, auth_headers):
        """PATCH /api/power-platform/actions/{id} - Update action"""
        if not TestPowerPlatformActions.created_action_id:
            pytest.skip("No action created to update")
        
        action_id = TestPowerPlatformActions.created_action_id
        response = requests.patch(
            f"{BASE_URL}/api/power-platform/actions/{action_id}",
            headers=auth_headers,
            json={
                "title": "TEST_Action_Updated",
                "status": "in_progress",
                "priority": "critical"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["title"] == "TEST_Action_Updated"
        assert data["status"] == "in_progress"
        assert data["priority"] == "critical"
    
    def test_delete_action(self, auth_headers):
        """DELETE /api/power-platform/actions/{id} - Delete action"""
        if not TestPowerPlatformActions.created_action_id:
            pytest.skip("No action created to delete")
        
        action_id = TestPowerPlatformActions.created_action_id
        response = requests.delete(
            f"{BASE_URL}/api/power-platform/actions/{action_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify deletion
        verify_response = requests.get(f"{BASE_URL}/api/power-platform/actions", headers=auth_headers)
        actions = verify_response.json()
        found = any(a["id"] == action_id for a in actions)
        assert not found, "Deleted action still found in list"


class TestPowerPlatformDecisions:
    """Test Power Platform decisions CRUD"""
    
    created_decision_id = None
    
    def test_get_decisions_list(self, auth_headers):
        """GET /api/power-platform/decisions - Get all decisions"""
        response = requests.get(f"{BASE_URL}/api/power-platform/decisions", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_decision(self, auth_headers):
        """POST /api/power-platform/decisions - Create new decision"""
        response = requests.post(
            f"{BASE_URL}/api/power-platform/decisions",
            headers=auth_headers,
            json={
                "decision_text": "TEST_Decision: We decided to implement governance framework",
                "workshop_number": 2,
                "evidence_links": ["https://example.com/doc1", "https://example.com/doc2"]
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "TEST_Decision" in data["decision_text"]
        assert data["workshop_number"] == 2
        assert len(data["evidence_links"]) == 2
        assert "id" in data
        
        # Store for later tests
        TestPowerPlatformDecisions.created_decision_id = data["id"]
        
        # Verify persistence
        verify_response = requests.get(f"{BASE_URL}/api/power-platform/decisions", headers=auth_headers)
        decisions = verify_response.json()
        found = any(d["id"] == data["id"] for d in decisions)
        assert found, "Created decision not found in list"
    
    def test_delete_decision(self, auth_headers):
        """DELETE /api/power-platform/decisions/{id} - Delete decision"""
        if not TestPowerPlatformDecisions.created_decision_id:
            pytest.skip("No decision created to delete")
        
        decision_id = TestPowerPlatformDecisions.created_decision_id
        response = requests.delete(
            f"{BASE_URL}/api/power-platform/decisions/{decision_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify deletion
        verify_response = requests.get(f"{BASE_URL}/api/power-platform/decisions", headers=auth_headers)
        decisions = verify_response.json()
        found = any(d["id"] == decision_id for d in decisions)
        assert not found, "Deleted decision still found in list"


class TestPowerPlatformDefinitions:
    """Test static definitions endpoints"""
    
    def test_get_workshop_definitions(self, auth_headers):
        """GET /api/power-platform/definitions/workshops - Get workshop definitions"""
        response = requests.get(f"{BASE_URL}/api/power-platform/definitions/workshops", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10, "Should have 10 workshop definitions"
    
    def test_get_item_definitions(self, auth_headers):
        """GET /api/power-platform/definitions/items - Get item definitions"""
        response = requests.get(f"{BASE_URL}/api/power-platform/definitions/items", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have item definitions"
    
    def test_get_item_definitions_filtered(self, auth_headers):
        """GET /api/power-platform/definitions/items?workshop_number=1 - Filter by workshop"""
        response = requests.get(f"{BASE_URL}/api/power-platform/definitions/items?workshop_number=1", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        for item in data:
            assert item["workshop_number"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
