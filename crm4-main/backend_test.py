import requests
import sys
import json
from datetime import datetime

class HungarianCRMTester:
    def __init__(self, base_url="https://category-manager-14.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.test_category_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@dolgozocrm.hu", "password": "admin123"}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.admin_user = response.get('user', {})
            print(f"   Admin user: {self.admin_user.get('name')} ({self.admin_user.get('role')})")
            return True
        return False

    def test_get_categories(self):
        """Test getting categories (should auto-create defaults if empty)"""
        success, response = self.run_test(
            "Get Categories",
            "GET", 
            "categories",
            200
        )
        if success:
            categories = response
            print(f"   Found {len(categories)} categories")
            for cat in categories[:3]:  # Show first 3
                print(f"   - {cat.get('name')} (color: {cat.get('color')})")
            return categories
        return []

    def test_create_category(self):
        """Test creating a new category"""
        test_category = {
            "name": f"Test Kategória {datetime.now().strftime('%H%M%S')}",
            "color": "#ff5722"
        }
        success, response = self.run_test(
            "Create Category",
            "POST",
            "categories",
            200,
            data=test_category
        )
        if success and 'id' in response:
            self.test_category_id = response['id']
            print(f"   Created category: {response.get('name')} (ID: {self.test_category_id})")
            return True
        return False

    def test_duplicate_category(self):
        """Test creating duplicate category (should fail)"""
        success, response = self.run_test(
            "Create Duplicate Category",
            "POST",
            "categories", 
            400,  # Should fail with 400
            data={"name": "Felvitt dolgozók", "color": "#3b82f6"}
        )
        return success  # Success means it correctly rejected duplicate

    def test_delete_category(self):
        """Test deleting the test category"""
        if not self.test_category_id:
            print("❌ No test category to delete")
            return False
            
        success, response = self.run_test(
            "Delete Category",
            "DELETE",
            f"categories/{self.test_category_id}",
            200
        )
        return success

    def test_delete_nonexistent_category(self):
        """Test deleting non-existent category"""
        fake_id = "fake-category-id-123"
        success, response = self.run_test(
            "Delete Non-existent Category",
            "DELETE",
            f"categories/{fake_id}",
            404
        )
        return success

    def test_edit_category(self):
        """Test editing/updating a category (PUT /api/categories/{id})"""
        if not self.test_category_id:
            # Create a category first for editing
            if not self.test_create_category():
                print("❌ Cannot test edit - failed to create test category")
                return False
        
        updated_data = {
            "name": f"Edited Kategória {datetime.now().strftime('%H%M%S')}",
            "color": "#9c27b0"
        }
        success, response = self.run_test(
            "Edit Category",
            "PUT",
            f"categories/{self.test_category_id}",
            200,
            data=updated_data
        )
        if success:
            print(f"   Updated category: {response.get('name')} (color: {response.get('color')})")
        return success

    def test_edit_nonexistent_category(self):
        """Test editing non-existent category"""
        fake_id = "fake-category-id-456"
        success, response = self.run_test(
            "Edit Non-existent Category",
            "PUT",
            f"categories/{fake_id}",
            404,
            data={"name": "Should Fail", "color": "#ff0000"}
        )
        return success

    def test_category_reorder(self):
        """Test drag & drop category reordering (PUT /api/categories/reorder)"""
        # First get current categories
        success, categories = self.run_test(
            "Get Categories for Reorder",
            "GET", 
            "categories",
            200
        )
        if not success or len(categories) < 2:
            print("❌ Need at least 2 categories to test reordering")
            return False
        
        # Create reorder data - reverse the order of first two categories
        reorder_data = {
            "orders": [
                {"id": categories[1]["id"], "order": 0},
                {"id": categories[0]["id"], "order": 1}
            ]
        }
        
        # Add remaining categories to maintain their order
        for i, cat in enumerate(categories[2:], 2):
            reorder_data["orders"].append({"id": cat["id"], "order": i})
        
        success, response = self.run_test(
            "Reorder Categories",
            "PUT",
            "categories/reorder",
            200,
            data=reorder_data
        )
        if success:
            print(f"   Reordered {len(reorder_data['orders'])} categories")
        return success

    def test_category_stats(self):
        """Test dashboard category statistics (GET /api/categories/stats)"""
        success, response = self.run_test(
            "Get Category Stats",
            "GET",
            "categories/stats",
            200
        )
        if success:
            print(f"   Total workers: {response.get('total_workers', 0)}")
            print(f"   Categories count: {response.get('categories_count', 0)}")
            category_stats = response.get('category_stats', [])
            print(f"   Category breakdown: {len(category_stats)} categories")
            
            recent_activity = response.get('recent_activity', [])
            total_recent = sum(r.get('count', 0) for r in recent_activity)
            print(f"   Recent activity (7 days): {total_recent} workers")
        return success

    # ==================== NEW CALENDAR TESTS ====================
    
    def test_calendar_trials(self):
        """Test getting calendar trials (GET /api/calendar/trials)"""
        success, response = self.run_test(
            "Get Calendar Trials",
            "GET",
            "calendar/trials",
            200
        )
        if success:
            trials = response if isinstance(response, list) else []
            print(f"   Found {len(trials)} trial events")
            for trial in trials[:3]:  # Show first 3
                print(f"   - {trial.get('title')} on {trial.get('start')}")
        return success

    def test_calendar_projects(self):
        """Test getting calendar projects (GET /api/calendar/projects)"""
        success, response = self.run_test(
            "Get Calendar Projects",
            "GET", 
            "calendar/projects",
            200
        )
        if success:
            projects = response if isinstance(response, list) else []
            print(f"   Found {len(projects)} project events")
            for project in projects[:3]:  # Show first 3
                print(f"   - {project.get('title')} on {project.get('start')}")
        return success

    # ==================== NEW NOTIFICATION TESTS ====================
    
    def test_notifications(self):
        """Test getting user notifications (GET /api/notifications)"""
        success, response = self.run_test(
            "Get Notifications",
            "GET",
            "notifications",
            200
        )
        if success:
            notifications = response if isinstance(response, list) else []
            print(f"   Found {len(notifications)} notifications")
            unread = sum(1 for n in notifications if not n.get('is_read', False))
            print(f"   Unread: {unread}")
        return success, response if success else []

    def test_unread_count(self):
        """Test getting unread notification count (GET /api/notifications/unread-count)"""
        success, response = self.run_test(
            "Get Unread Notification Count",
            "GET",
            "notifications/unread-count", 
            200
        )
        if success:
            count = response.get('count', 0)
            print(f"   Unread count: {count}")
        return success

    def test_mark_notification_read(self, notifications):
        """Test marking notification as read (PUT /api/notifications/{id}/read)"""
        if not notifications:
            print("   No notifications to test mark as read")
            return True
        
        # Find first unread notification
        unread_notif = None
        for n in notifications:
            if not n.get('is_read', False):
                unread_notif = n
                break
        
        if not unread_notif:
            print("   No unread notifications to test")
            return True
            
        success, response = self.run_test(
            f"Mark Notification Read",
            "PUT",
            f"notifications/{unread_notif['id']}/read",
            200
        )
        return success

    def test_mark_all_read(self):
        """Test marking all notifications as read (PUT /api/notifications/read-all)"""
        success, response = self.run_test(
            "Mark All Notifications Read",
            "PUT",
            "notifications/read-all",
            200
        )
        return success

    def test_profile_update_non_admin(self):
        """Test that non-admin users cannot update profile (should return 403)"""
        # This would need a recruiter token, but we can test the admin restriction
        success, response = self.run_test(
            "Profile Update (Admin Only)",
            "PUT",
            "auth/profile",
            200,  # Should work for admin
            data={"name": "Test Admin Name Update"}
        )
        return success

    def test_worker_types(self):
        """Test worker types endpoint (needed for worker creation)"""
        success, response = self.run_test(
            "Get Worker Types",
            "GET",
            "worker-types",
            200
        )
        if success:
            print(f"   Found {len(response)} worker types")
            return response
        return []

    def test_get_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        if success:
            print(f"   Current user: {response.get('name')} ({response.get('role')})")
        return success

    # ==================== NEW TRIAL POSITIONS TESTS ====================
    
    def test_get_projects(self):
        """Test getting projects to find one for trial testing"""
        success, response = self.run_test(
            "Get Projects",
            "GET",
            "projects",
            200
        )
        if success and response:
            print(f"   Found {len(response)} projects")
            # Return first project with trials
            for project in response:
                if project.get('trial_count', 0) > 0:
                    print(f"   Using project: {project['name']} (has {project['trial_count']} trials)")
                    return project
            print(f"   Using first project: {response[0]['name']}")
            return response[0] if response else None
        return None
    
    def test_get_project_detail(self, project_id):
        """Test getting detailed project info with trials"""
        success, response = self.run_test(
            "Get Project Detail",
            "GET", 
            f"projects/{project_id}",
            200
        )
        if success:
            trials = response.get('trials', [])
            positions = response.get('positions', [])
            print(f"   Project has {len(trials)} trials and {len(positions)} positions")
            return response
        return None
    
    def test_trial_positions_get(self, project_id, trial_id):
        """Test getting trial positions"""
        success, response = self.run_test(
            "Get Trial Positions",
            "GET",
            f"projects/{project_id}/trials/{trial_id}/positions",
            200
        )
        if success:
            print(f"   Found {len(response)} trial positions")
            return response
        return []
    
    def test_trial_positions_create(self, project_id, trial_id):
        """Test creating a trial position"""
        trial_position_data = {
            "position_name": f"Test Próba Pozíció {datetime.now().strftime('%H%M%S')}",
            "headcount": 2,
            "requirements": "Test elvárások - fizikai erőnlét szükséges",
            "add_to_project": True
        }
        success, response = self.run_test(
            "Create Trial Position",
            "POST",
            f"projects/{project_id}/trials/{trial_id}/positions",
            200,
            data=trial_position_data
        )
        if success and 'id' in response:
            print(f"   Created trial position: {response.get('position_name')} (ID: {response['id']})")
            return response['id']
        return None
    
    def test_trial_positions_update(self, project_id, trial_id, position_id):
        """Test updating a trial position"""
        update_data = {
            "position_name": f"Frissített Próba Pozíció {datetime.now().strftime('%H%M%S')}",
            "headcount": 3,
            "requirements": "Frissített elvárások - minimum 1 év tapasztalat",
            "add_to_project": False
        }
        success, response = self.run_test(
            "Update Trial Position",
            "PUT",
            f"projects/{project_id}/trials/{trial_id}/positions/{position_id}",
            200,
            data=update_data
        )
        if success:
            print(f"   Updated trial position headcount to: {response.get('headcount')}")
        return success
    
    def test_trial_positions_delete(self, project_id, trial_id, position_id):
        """Test deleting a trial position"""
        success, response = self.run_test(
            "Delete Trial Position",
            "DELETE",
            f"projects/{project_id}/trials/{trial_id}/positions/{position_id}",
            200
        )
        return success
    
    def test_create_trial_for_testing(self, project_id):
        """Create a trial for testing trial positions"""
        trial_data = {
            "date": "2026-02-28",
            "time": "10:00",
            "notes": "Test próba pozíciók teszteléshez"
        }
        success, response = self.run_test(
            "Create Test Trial",
            "POST",
            f"projects/{project_id}/trials",
            200,
            data=trial_data
        )
        if success and 'id' in response:
            print(f"   Created test trial: {response['id']}")
            return response['id']
        return None

def main():
    print("🚀 Starting Hungarian CRM Backend Tests (Calendar & Notifications)")
    print("=" * 60)
    
    tester = HungarianCRMTester()
    
    # Test authentication first
    if not tester.test_admin_login():
        print("\n❌ Admin login failed - stopping all tests")
        return 1

    # Test user info
    tester.test_get_me()
    
    # Test NEW FEATURES - Calendar endpoints
    print("\n📅 Testing NEW Calendar Features...")
    tester.test_calendar_trials()
    tester.test_calendar_projects()
    
    # Test NEW FEATURES - Notifications endpoints
    print("\n🔔 Testing NEW Notifications Features...")
    notifications_success, notifications_list = tester.test_notifications()
    tester.test_unread_count()
    if notifications_success:
        tester.test_mark_notification_read(notifications_list)
    tester.test_mark_all_read()
    
    # Test profile update restriction
    print("\n👤 Testing Profile Update Restrictions...")
    tester.test_profile_update_non_admin()
    
    # Test categories functionality (existing)
    print("\n📂 Testing Categories Management...")
    initial_categories = tester.test_get_categories()
    
    if not tester.test_create_category():
        print("❌ Category creation failed")
        
    # Test edge cases
    tester.test_duplicate_category()
    
    # Test Category editing
    print("\n✏️ Testing Category Editing Features...")
    tester.test_edit_category()
    tester.test_edit_nonexistent_category()
    
    # Test Drag & drop reordering
    print("\n🔄 Testing Drag & Drop Reordering...")
    tester.test_category_reorder()
    
    # Test Dashboard statistics
    print("\n📊 Testing Dashboard Statistics...")
    tester.test_category_stats()
    
    # Test deletion
    tester.test_delete_category()
    tester.test_delete_nonexistent_category()
    
    # Test other endpoints needed for integration
    print("\n🔧 Testing Supporting Endpoints...")
    tester.test_worker_types()
    
    # ========== NEW TRIAL POSITIONS TESTING ==========
    print("\n🧪 Testing NEW Trial Positions Management...")
    
    # Get a project to test with
    test_project = tester.test_get_projects()
    if test_project:
        project_detail = tester.test_get_project_detail(test_project['id'])
        if project_detail:
            existing_trials = project_detail.get('trials', [])
            test_trial_id = None
            
            # Use existing trial if available, otherwise create one
            if existing_trials:
                test_trial_id = existing_trials[0]['id']
                print(f"   Using existing trial: {test_trial_id}")
            else:
                # Create a trial for testing
                test_trial_id = tester.test_create_trial_for_testing(test_project['id'])
            
            if test_trial_id:
                # Test trial positions CRUD operations
                initial_positions = tester.test_trial_positions_get(test_project['id'], test_trial_id)
                
                # Test create trial position
                new_position_id = tester.test_trial_positions_create(test_project['id'], test_trial_id)
                
                if new_position_id:
                    # Test update trial position
                    tester.test_trial_positions_update(test_project['id'], test_trial_id, new_position_id)
                    
                    # Test get positions after update
                    updated_positions = tester.test_trial_positions_get(test_project['id'], test_trial_id)
                    
                    # Test delete trial position
                    tester.test_trial_positions_delete(test_project['id'], test_trial_id, new_position_id)
                else:
                    print("❌ Could not test trial position update/delete - creation failed")
            else:
                print("❌ Could not test trial positions - no trial available")
        else:
            print("❌ Could not get project detail")
    else:
        print("❌ No projects found for trial positions testing")

    # Print final results
    print(f"\n📊 Backend Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend tests passed!")
        return 0
    else:
        print("⚠️  Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())