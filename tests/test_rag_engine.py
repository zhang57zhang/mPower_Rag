"""
Unit tests for RAG engine (English only to avoid encoding issues)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simple_config import Document
from simple_rag_engine import EnhancedRAGEngine
from local_vector_store import LocalVectorStore


def test_rag_engine_initialization():
    """Test RAG engine initialization"""
    print("=" * 60)
    print("Test: RAG Engine Initialization")
    print("=" * 60)

    # Create engine without vector search
    print("\n1. Creating RAG engine (no vector search)...")
    engine = EnhancedRAGEngine(use_vector=False)
    assert engine is not None
    print("   OK - Engine created")

    # Initialize
    print("\n2. Initializing engine...")
    success = engine.initialize()
    assert success == True
    assert engine.is_initialized == True
    print("   OK - Engine initialized")

    # Health check
    print("\n3. Health check...")
    health = engine.health_check()
    assert health['status'] == 'healthy'
    print("   OK - Health check passed")

    print("\n" + "=" * 60)
    print("PASSED!")
    print("=" * 60)

    return True


def test_rag_engine_add_documents():
    """Test adding documents to RAG engine"""
    print("\n" + "=" * 60)
    print("Test: Add Documents")
    print("=" * 60)

    # Create and initialize engine
    engine = EnhancedRAGEngine(use_vector=False)
    engine.initialize()

    # Setup vector store
    print("\n1. Setting up local vector store...")
    engine.vector_engine = LocalVectorStore()
    engine.vector_engine.backend_type = 'local_tfidf'
    print("   OK - Local vector store ready")

    # Add documents
    print("\n2. Adding documents...")
    documents = [
        Document(
            "Bluetooth testing includes device discovery, pairing and connection verification",
            metadata={"source": "bluetooth.txt"}
        ),
        Document(
            "ECU diagnosis reads fault codes and real-time data from OBD interface",
            metadata={"source": "ecu.txt"}
        ),
        Document(
            "CAN bus testing verifies data frame integrity and timing",
            metadata={"source": "can.txt"}
        )
    ]

    engine.add_documents(documents)
    assert len(engine.documents) == 3
    print(f"   OK - Added {len(engine.documents)} documents")

    # Check vector store
    print("\n3. Checking vector store...")
    vector_info = engine.vector_engine.get_info()
    assert vector_info['document_count'] == 3
    print(f"   OK - Vector store has {vector_info['document_count']} documents")

    print("\n" + "=" * 60)
    print("PASSED!")
    print("=" * 60)

    return True


def test_rag_engine_search():
    """Test search functionality"""
    print("\n" + "=" * 60)
    print("Test: Search Functionality")
    print("=" * 60)

    # Create and initialize engine
    engine = EnhancedRAGEngine(use_vector=False)
    engine.initialize()
    engine.vector_engine = LocalVectorStore()
    engine.vector_engine.backend_type = 'local_tfidf'

    # Add test documents
    documents = [
        Document("Bluetooth testing", {"source": "test.txt"}),
        Document("ECU diagnosis", {"source": "test.txt"}),
        Document("CAN bus testing", {"source": "test.txt"})
    ]
    engine.add_documents(documents)

    # Test search
    print("\n1. Testing search...")
    results = engine.search_similar("bluetooth", top_k=2)
    assert isinstance(results, list)
    assert len(results) <= 2
    print(f"   OK - Search returned {len(results)} results")

    if results:
        print(f"      Top result score: {results[0].get('score', 0):.3f}")
        print(f"      Top result content: {results[0]['content'][:50]}...")

    # Test keyword search fallback
    print("\n2. Testing keyword search...")
    results = engine._keyword_search("bluetooth", top_k=2)
    assert isinstance(results, list)
    print(f"   OK - Keyword search returned {len(results)} results")

    print("\n" + "=" * 60)
    print("PASSED!")
    print("=" * 60)

    return True


def test_rag_engine_query():
    """Test query with sources"""
    print("\n" + "=" * 60)
    print("Test: Query with Sources")
    print("=" * 60)

    # Create and initialize engine
    engine = EnhancedRAGEngine(use_vector=False)
    engine.initialize()
    engine.vector_engine = LocalVectorStore()
    engine.vector_engine.backend_type = 'local_tfidf'

    # Add test documents
    documents = [
        Document("Bluetooth test steps: 1. Device discovery, 2. Pairing, 3. Connection", {"source": "bt.txt"}),
        Document("ECU diagnosis uses OBD to read DTC codes", {"source": "ecu.txt"})
    ]
    engine.add_documents(documents)

    # Test query without LLM
    print("\n1. Testing query (no LLM)...")
    result = engine.query_with_sources("bluetooth", use_llm=False)
    assert 'answer' in result
    assert 'sources' in result
    assert 'query' in result
    assert result['query'] == 'bluetooth'
    print(f"   OK - Query returned answer and {len(result['sources'])} sources")

    print(f"      Answer preview: {result['answer'][:100]}...")

    print("\n" + "=" * 60)
    print("PASSED!")
    print("=" * 60)

    return True


def run_all_tests():
    """Run all RAG engine tests"""
    print("\n" + "=" * 70)
    print("RAG Engine Test Suite")
    print("=" * 70)

    tests = [
        ("Initialization", test_rag_engine_initialization),
        ("Add Documents", test_rag_engine_add_documents),
        ("Search", test_rag_engine_search),
        ("Query", test_rag_engine_query)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"\n--- Running: {name} ---")
            test_func()
            passed += 1
            print(f"[PASS] {name}: PASSED")
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {name}: FAILED - {e}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {name}: FAILED - {e}")
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
        print("\nAll tests PASSED!")
        return True
    else:
        print(f"\n{failed} test(s) FAILED")
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
