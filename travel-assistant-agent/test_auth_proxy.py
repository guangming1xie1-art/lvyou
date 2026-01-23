#!/usr/bin/env python3
"""
Agent认证端点测试脚本

测试Agent层的认证代理功能
"""
import asyncio
import httpx
import json
import time

# 配置
AGENT_URL = "http://localhost:8000"
JAVA_AUTH_URL = "http://localhost:8080/api/auth"

class AuthTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_user = {
            "username": "agenttest",
            "email": "agenttest@example.com",
            "password": "AgentTest123!@",
            "confirm_password": "AgentTest123!@"
        }
        self.access_token = None
        self.refresh_token = None

    async def test_register(self):
        """测试注册功能"""
        print("🧪 Testing Register...")
        try:
            response = await self.client.post(
                f"{AGENT_URL}/api/auth/register",
                json=self.test_user
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Register failed: {e}")
            return False

    async def test_login(self):
        """测试登录功能"""
        print("🧪 Testing Login...")
        try:
            login_data = {
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
            response = await self.client.post(
                f"{AGENT_URL}/api/auth/login",
                json=login_data
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200:
                data = response.json()
                if "tokens" in data:
                    self.access_token = data["tokens"].get("access_token")
                    self.refresh_token = data["tokens"].get("refresh_token")
                return True
            return False
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    async def test_get_current_user(self):
        """测试获取当前用户"""
        print("🧪 Testing Get Current User...")
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            response = await self.client.get(
                f"{AGENT_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Get current user failed: {e}")
            return False

    async def test_refresh_token(self):
        """测试刷新token"""
        print("🧪 Testing Refresh Token...")
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        try:
            response = await self.client.post(
                f"{AGENT_URL}/api/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Refresh token failed: {e}")
            return False

    async def test_logout(self):
        """测试登出"""
        print("🧪 Testing Logout...")
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            response = await self.client.post(
                f"{AGENT_URL}/api/auth/logout",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Logout failed: {e}")
            return False

    async def test_java_api_health(self):
        """测试Java API健康状态"""
        print("🧪 Testing Java Auth Service Health...")
        try:
            # 先检查Java auth-service是否可用
            response = await self.client.get(f"{JAVA_AUTH_URL}/health")
            print(f"Java auth-service health: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Java auth-service not available: {e}")
            print("💡 Make sure to start Java auth-service first: cd travel-assistant/auth-service && mvn spring-boot:run")
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 Starting Agent Auth Proxy Tests")
        print("=" * 50)
        
        # 测试Java API健康状态
        java_healthy = await self.test_java_api_health()
        if not java_healthy:
            print("\n❌ Cannot proceed without Java auth-service")
            return False
        
        print("\n" + "=" * 50)
        
        tests = [
            ("Register", self.test_register),
            ("Login", self.test_login),
            ("Get Current User", self.test_get_current_user),
            ("Refresh Token", self.test_refresh_token),
            ("Logout", self.test_logout)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} test...")
            try:
                result = await test_func()
                results[test_name] = result
                if result:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"💥 {test_name} CRASHED: {e}")
                results[test_name] = False
        
        # 总结
        print("\n" + "=" * 50)
        print("🏁 Test Results Summary:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        passed = sum(results.values())
        total = len(results)
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Agent auth proxy is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the logs above.")
        
        return passed == total

async def main():
    tester = AuthTester()
    await tester.run_all_tests()
    await tester.client.aclose()

if __name__ == "__main__":
    print("Agent Auth Proxy Test Suite")
    print("This script tests the authentication proxy endpoints.")
    print("\nPrerequisites:")
    print("1. Start Java auth-service: cd travel-assistant/auth-service && mvn spring-boot:run")
    print("2. Start Agent: cd travel-assistant-agent && python -m uvicorn src.main:app --reload")
    print("\nStarting tests...")
    
    asyncio.run(main())