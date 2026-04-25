#!/usr/bin/env python
"""Health check script for system connectivity."""
import httpx
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"


def check_api():
    """Check API health."""
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        if response.status_code == 200:
            print("✅ API: OK")
            return True
    except Exception as e:
        print(f"❌ API: FAILED ({e})")
        return False


def check_admin_health():
    """Check admin health endpoint."""
    try:
        response = httpx.get(f"{BASE_URL}/admin/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            db_status = data.get("database", "unknown")
            redis_status = data.get("redis", "unknown")
            neo4j_status = data.get("neo4j", "unknown")

            print(f"✅ Admin Health: OK")
            print(f"   └─ Database: {db_status}")
            print(f"   └─ Redis: {redis_status}")
            print(f"   └─ Neo4j: {neo4j_status}")
            return True
    except Exception as e:
        print(f"❌ Admin Health: FAILED ({e})")
        return False


def check_endpoints():
    """Check key endpoints."""
    endpoints = [
        ("GET", "/shipments"),
        ("GET", "/events"),
        ("GET", "/admin/dashboard"),
    ]

    try:
        for method, endpoint in endpoints:
            response = httpx.get(f"{BASE_URL}{endpoint}", timeout=5.0)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {method} {endpoint}: {response.status_code}")
    except Exception as e:
        print(f"❌ Endpoint checks failed: {e}")


def main():
    """Main health check."""
    print("=" * 50)
    print(f"Supply Chain System Health Check")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 50)
    print()

    print("🔍 Checking API connectivity...")
    api_ok = check_api()
    print()

    if api_ok:
        print("🔍 Checking system components...")
        check_admin_health()
        print()

        print("🔍 Checking endpoints...")
        check_endpoints()
        print()

        print("=" * 50)
        print("✅ System appears healthy!")
        print("=" * 50)
    else:
        print("=" * 50)
        print("❌ API is not responding. Check if server is running.")
        print("=" * 50)


if __name__ == "__main__":
    main()
