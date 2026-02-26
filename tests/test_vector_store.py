"""
Unit tests for vector search engines
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from local_vector_store import LocalVectorStore
from simple_config import Document


def test_local_vector_store():
    """Test local TF-IDF vector store"""
    print("=" * 60)
    print("Test: Local Vector Store")
    print("=" * 60)

    # Create vector store
    print("\n1. Creating vector store...")
    store = LocalVectorStore()
    assert store is not None
    print("   OK - Vector store created")

    # Add documents
    print("\n2. Adding documents...")
    documents = [
        {
            "id": "doc1",
            "content": "Bluetooth testing includes device discovery and pairing",
            "source": "test.txt",
            "metadata": {}
        },
        {
            "id": "doc2",
            "content": "ECU diagnosis reads fault codes from OBD interface",
            "source": "test.txt",
            "metadata": {}
        },
        {
            "id": "doc3",
            "content": "CAN bus testing verifies data frame integrity",
            "source": "test.txt",
            "metadata": {}
        }
    ]

    success = store.add_documents(documents)
    assert success == True
    assert len(store.documents) == 3
    print(f"   OK - Added {len(store.documents)} documents")

    # Test search
    print("\n3. Testing search...")
    results = store.search("bluetooth", top_k=2)
    assert len(results) <= 2
    print(f"   OK - Search returned {len(results)} results")

    if results:
        print(f"      Top result: {results[0]['content'][:50]}...")
        assert "bluetooth" in results[0]['content'].lower()

    # Test non-existent query
    print("\n4. Testing non-existent query...")
    results = store.search("xyz123", top_k=5)
    # May return results with low scores, that's OK
    print(f"   OK - Non-existent query returned {len(results)} results")

    # Test get_info
    print("\n5. Testing get_info...")
    info = store.get_info()
    assert info['document_count'] == 3
    assert info['vector_count'] == 3
    assert info['storage_type'] == 'local_tfidf'
    print(f"   OK - Info: {info}")

    # Test clear
    print("\n6. Testing clear...")
    store.clear()
    assert len(store.documents) == 0
    assert len(store.document_vectors) == 0
    print("   OK - Store cleared")

    print("\n" + "=" * 60)
    print("All tests PASSED!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_local_vector_store()
        print("\nTest suite: SUCCESS")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTest suite: FAILED")
        print(f"Assertion error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest suite: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
