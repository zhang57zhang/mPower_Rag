"""
Unit tests for API endpoints
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import json


def test_api_health():
    """Test API health endpoint"""
    print("=" * 60)
    print("Test: API Health Check")
    print("=" * 60)

    base_url = "http://localhost:8000"

    try:
        print("\n1. Testing /health endpoint...")
        response = httpx.get(f"{base_url}/health", timeout=5)

        assert response.status_code == 200
        print(f"   OK - Status code: {response.status_code}")

        data = response.json()
        assert 'status' in data
        print(f"   OK - Status: {data['status']}")

        print("\n2. Testing / root endpoint...")
        response = httpx.get(f"{base_url}/", timeout=5)
        assert response.status_code == 200
        print(f"   OK - Status code: {response.status_code}")

        print("\n" + "=" * 60)
        print("PASSED!")
        print("=" * 60)

        return True

    except httpx.ConnectError:
        print("\n✗ Connection failed - API server may not be running")
        print("   Start API with: python simple_api.py")
        return False
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


def test_api_chat():
    """Test API chat endpoint"""
    print("\n" + "=" * 60)
    print("Test: API Chat Endpoint")
    print("=" * 60)

    base_url = "http://localhost:8000"

    try:
        print("\n1. Testing /api/v1/chat endpoint...")
        query = "bluetooth testing"

        payload = {
            "query": query,
            "use_rerank": False,
            "top_k": 3
        }

        response = httpx.post(
            f"{base_url}/api/v1/chat",
            json=payload,
            timeout=30
        )

        assert response.status_code == 200
        print(f"   OK - Status code: {response.status_code}")

        data = response.json()
        assert 'answer' in data
        assert 'sources' in data
        assert 'query' in data

        print(f"   OK - Response has answer and sources")
        print(f"      Query: {data['query']}")
        print(f"      Answer preview: {data['answer'][:100]}...")
        print(f"      Sources count: {len(data['sources'])}")

        print("\n2. Testing with different query...")
        payload["query"] = "ECU diagnosis"
        response = httpx.post(
            f"{base_url}/api/v1/chat",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200
        print(f"   OK - Second query successful")

        print("\n" + "=" * 60)
        print("PASSED!")
        print("=" * 60)

        return True

    except httpx.ConnectError:
        print("\n✗ Connection failed - API server may not be running")
        print("   Start API with: python simple_api.py")
        return False
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_document_stats():
    """Test document statistics endpoint"""
    print("\n" + "=" * 60)
    print("Test: Document Statistics")
    print("=" * 60)

    base_url = "http://localhost:8000"

    try:
        print("\n1. Testing /api/v1/documents/stats endpoint...")
        response = httpx.get(
            f"{base_url}/api/v1/documents/stats",
            timeout=5
        )

        assert response.status_code == 200
        print(f"   OK - Status code: {response.status_code}")

        data = response.json()
        assert 'total_documents' in data
        assert 'total_chunks' in data

        print(f"   OK - Document statistics retrieved")
        print(f"      Total documents: {data['total_documents']}")
        print(f"      Total chunks: {data['total_chunks']}")

        print("\n" + "=" * 60)
        print("PASSED!")
        print("=" * 60)

        return True

    except httpx.ConnectError:
        print("\n✗ Connection failed - API server may not be running")
        return False
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


def test_api_examples():
    """Test examples endpoint"""
    print("\n" + "=" * 60)
    print("Test: Examples Endpoint")
    print("=" * 60)

    base_url = "http://localhost:8000"

    try:
        print("\n1. Testing /api/v1/examples endpoint...")
        response = httpx.get(
            f"{base_url}/api/v1/examples",
            timeout=5
        )

        assert response.status_code == 200
        print(f"   OK - Status code: {response.status_code}")

        data = response.json()
        assert 'examples' in data
        assert isinstance(data['examples'], list)

        print(f"   OK - Examples retrieved")
        print(f"      Count: {len(data['examples'])}")

        if data['examples']:
            print(f"      First example: {data['examples'][0]}")

        print("\n" + "=" * 60)
        print("PASSED!")
        print("=" * 60)

        return True

    except httpx.ConnectError:
        print("\n✗ Connection failed - API server may not be running")
        return False
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("\n" + "=" * 70)
    print("API Test Suite")
    print("=" * 70)

    tests = [
        ("Health Check", test_api_health),
        ("Chat Endpoint", test_api_chat),
        ("Document Stats", test_api_document_stats),
        ("Examples", test_api_examples)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"\n--- Running: {name} ---")
            success = test_func()
            if success:
                passed += 1
                print(f"✓ {name}: PASSED")
            else:
                failed += 1
                print(f"✗ {name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {name}: FAILED - {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total: {len(tests)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 All tests PASSED!")
        return True
    else:
        print(f"\n❌ {failed} test(s) FAILED")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTest suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
