#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class Bizdesk365APITester:
    def __init__(self, base_url="https://compliancepro-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.failed_tests.append({"test": name, "error": details})

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                self.log_test(name, False, error_msg)
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_login(self):
        """Test login with demo credentials"""
        success, response = self.run_test(
            "Login with demo credentials",
            "POST",
            "auth/login",
            200,
            data={"email": "demo@bizdesk365.local", "password": "demo"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_get_user_info(self):
        """Test getting current user info"""
        success, response = self.run_test("Get User Info", "GET", "me", 200)
        
        if success:
            print(f"   User: {response.get('email', 'N/A')}")
            print(f"   Tenant ID: {response.get('tenant_id', 'N/A')}")
            print(f"   Roles: {response.get('roles', [])}")
        
        return success

    def test_get_modules(self):
        """Test getting modules"""
        success, response = self.run_test("Get Modules", "GET", "modules", 200)
        
        if success:
            modules = response if isinstance(response, list) else []
            print(f"   Found {len(modules)} modules")
            enabled_count = sum(1 for m in modules if m.get('enabled', False))
            disabled_count = len(modules) - enabled_count
            print(f"   Enabled: {enabled_count}, Disabled: {disabled_count}")
            
            # Check if we have expected 5 modules (4 enabled, 1 disabled)
            if len(modules) == 5 and enabled_count == 4 and disabled_count == 1:
                print("   ✓ Module count matches expected (5 total, 4 enabled, 1 disabled)")
            else:
                print(f"   ⚠ Module count mismatch - Expected 5 total (4 enabled, 1 disabled)")
        
        return success

    def test_compliance_kpis(self):
        """Test compliance KPIs endpoint"""
        success, response = self.run_test("Get Compliance KPIs", "GET", "compliance/kpis/latest", 200)
        
        if success:
            kpis = response if isinstance(response, list) else []
            print(f"   Found {len(kpis)} KPIs")
            if len(kpis) >= 3:
                print("   ✓ Expected KPI count (3+)")
            else:
                print(f"   ⚠ Expected at least 3 KPIs, got {len(kpis)}")
        
        return success

    def test_compliance_maturity(self):
        """Test compliance maturity endpoint"""
        success, response = self.run_test("Get Compliance Maturity", "GET", "compliance/maturity", 200)
        
        if success:
            score = response.get('score', 0)
            band = response.get('band', 'unknown')
            iso_refs = response.get('iso_referentials', [])
            print(f"   Maturity Score: {score}")
            print(f"   Band: {band}")
            print(f"   ISO Referentials: {len(iso_refs)}")
        
        return success

    def test_enterprise_brain_quality(self):
        """Test enterprise brain quality endpoint"""
        success, response = self.run_test("Get Enterprise Brain Quality", "GET", "enterprise-brain/quality", 200)
        
        if success:
            iqi_global = response.get('iqi_global', 0)
            evidences = response.get('evidences', {})
            print(f"   IQI Global: {iqi_global}")
            print(f"   Total Documents: {evidences.get('total_documents', 0)}")
        
        return success

    def test_enterprise_brain_documents(self):
        """Test enterprise brain documents endpoint"""
        success, response = self.run_test("Get Enterprise Brain Documents", "GET", "enterprise-brain/documents", 200)
        
        if success:
            docs = response if isinstance(response, list) else []
            print(f"   Found {len(docs)} documents")
            if len(docs) >= 4:
                print("   ✓ Expected document count (4+)")
            else:
                print(f"   ⚠ Expected at least 4 documents, got {len(docs)}")
        
        return success

    def test_ai_usage_document(self):
        """Test AI usage for specific document"""
        success, response = self.run_test("Get AI Usage for Document", "GET", "ai/usage/document/doc-001", 200)
        
        if success:
            status = response.get('usage_status', 'unknown')
            iqi_score = response.get('iqi_score', 0)
            print(f"   Usage Status: {status}")
            print(f"   IQI Score: {iqi_score}")
            if status in ['authorized', 'assisted', 'forbidden']:
                print("   ✓ Valid usage status")
            else:
                print(f"   ⚠ Unexpected usage status: {status}")
        
        return success

    def test_ai_governance_summary(self):
        """Test AI governance summary endpoint"""
        success, response = self.run_test("Get AI Governance Summary", "GET", "governance/ai/summary", 200)
        
        if success:
            auth_pct = response.get('authorized_percentage', 0)
            assist_pct = response.get('assisted_percentage', 0)
            forbid_pct = response.get('forbidden_percentage', 0)
            total = response.get('total_usages', 0)
            actions = response.get('critical_actions', [])
            
            print(f"   Authorized: {auth_pct}%")
            print(f"   Assisted: {assist_pct}%")
            print(f"   Forbidden: {forbid_pct}%")
            print(f"   Total Usages: {total}")
            print(f"   Critical Actions: {len(actions)}")
        
        return success

    def test_settings_iso(self):
        """Test ISO settings endpoints"""
        # Get ISO profiles
        success, response = self.run_test("Get ISO Profiles", "GET", "settings/iso", 200)
        
        if success:
            profiles = response if isinstance(response, list) else []
            print(f"   Found {len(profiles)} ISO profiles")
            if len(profiles) >= 4:
                print("   ✓ Expected ISO profile count (4+)")
            else:
                print(f"   ⚠ Expected at least 4 ISO profiles, got {len(profiles)}")
            
            # Test updating ISO profiles
            if profiles:
                update_data = {"profiles": profiles}  # Keep same data for test
                update_success, _ = self.run_test("Update ISO Profiles", "PUT", "settings/iso", 200, data=update_data)
                return success and update_success
        
        return success

    def test_settings_ai_policy(self):
        """Test AI policy settings endpoints"""
        # Get AI policy
        success, response = self.run_test("Get AI Policy", "GET", "settings/ai-policy", 200)
        
        if success:
            min_auth = response.get('min_iqi_authorized', 0)
            min_assist = response.get('min_iqi_assisted', 0)
            print(f"   Min IQI Authorized: {min_auth}")
            print(f"   Min IQI Assisted: {min_assist}")
            
            # Test updating AI policy
            update_data = {
                "min_iqi_authorized": min_auth,
                "min_iqi_assisted": min_assist
            }
            update_success, _ = self.run_test("Update AI Policy", "PUT", "settings/ai-policy", 200, data=update_data)
            return success and update_success
        
        return success

    def test_power_platform_health(self):
        """Test Power Platform health endpoint"""
        success, response = self.run_test("Get Power Platform Health", "GET", "power-platform/health", 200)
        
        if success:
            status = response.get('status', 'unknown')
            message = response.get('message', '')
            enabled = response.get('module_enabled', False)
            print(f"   Status: {status}")
            print(f"   Module Enabled: {enabled}")
            if status == 'coming_soon':
                print("   ✓ Expected coming_soon status")
            else:
                print(f"   ⚠ Expected 'coming_soon' status, got '{status}'")
        
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Bizdesk365 API Tests")
        print("=" * 50)
        
        # Test health first
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False
        
        # Test authentication
        if not self.test_login():
            print("❌ Login failed - stopping tests")
            return False
        
        # Test authenticated endpoints
        test_methods = [
            self.test_get_user_info,
            self.test_get_modules,
            self.test_compliance_kpis,
            self.test_compliance_maturity,
            self.test_enterprise_brain_quality,
            self.test_enterprise_brain_documents,
            self.test_ai_usage_document,
            self.test_ai_governance_summary,
            self.test_settings_iso,
            self.test_settings_ai_policy,
            self.test_power_platform_health
        ]
        
        for test_method in test_methods:
            test_method()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failed in self.failed_tests:
                print(f"   - {failed['test']}: {failed['error']}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = Bizdesk365APITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())