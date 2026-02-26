"""
Performance tests for RAG system
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from simple_config import Document
from simple_rag_engine import EnhancedRAGEngine
from local_vector_store import LocalVectorStore


class PerformanceTest:
    """Performance test utilities"""

    def __init__(self):
        self.results = []

    def measure_time(self, name, func):
        """Measure execution time of a function"""
        start_time = time.time()
        result = func()
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000  # Convert to ms

        self.results.append({
            'name': name,
            'time_ms': elapsed,
            'result': result
        })

        print(f"  {name}: {elapsed:.2f} ms")
        return result, elapsed

    def print_summary(self):
        """Print performance summary"""
        print("\n" + "=" * 70)
        print("Performance Summary")
        print("=" * 70)

        for result in self.results:
            print(f"{result['name']:40s}: {result['time_ms']:8.2f} ms")

        # Calculate statistics
        times = [r['time_ms'] for r in self.results]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\nAverage: {avg_time:.2f} ms")
        print(f"Min: {min_time:.2f} ms")
        print(f"Max: {max_time:.2f} ms")


def test_initialization_performance():
    """Test engine initialization performance"""
    print("=" * 60)
    print("Performance Test: Initialization")
    print("=" * 60)

    perf = PerformanceTest()

    # Test initialization
    print("\n1. Measuring initialization time...")
    def init_engine():
        engine = EnhancedRAGEngine(use_vector=False)
        engine.initialize()
        return engine

    engine, init_time = perf.measure_time("Engine initialization", init_engine)

    # Test vector store creation
    print("\n2. Measuring vector store creation time...")
    def create_vector_store():
        return LocalVectorStore()

    vector_store, store_time = perf.measure_time("Vector store creation", create_vector_store)

    perf.print_summary()

    # Assertions
    assert init_time < 5000, f"Initialization too slow: {init_time} ms"
    assert store_time < 1000, f"Vector store creation too slow: {store_time} ms"

    print("\n[OK] Performance targets met")

    return True


def test_add_documents_performance():
    """Test document addition performance"""
    print("\n" + "=" * 60)
    print("Performance Test: Add Documents")
    print("=" * 60)

    # Create engine
    engine = EnhancedRAGEngine(use_vector=False)
    engine.initialize()
    engine.vector_engine = LocalVectorStore()
    engine.vector_engine.backend_type = 'local_tfidf'

    perf = PerformanceTest()

    # Test different batch sizes
    batch_sizes = [10, 50, 100]

    for batch_size in batch_sizes:
        # Generate documents
        documents = []
        for i in range(batch_size):
            documents.append(Document(
                f"Test document {i} with some content about testing automotive systems",
                {"source": "test.txt"}
            ))

        print(f"\n{len(documents)} documents...")

        def add_batch():
            engine.add_documents(documents)
            return len(documents)

        perf.measure_time(f"Add {batch_size} documents", add_batch)

    perf.print_summary()

    return True


def test_search_performance():
    """Test search performance"""
    print("\n" + "=" * 60)
    print("Performance Test: Search")
    print("=" * 60)

    # Create and populate engine
    engine = EnhancedRAGEngine(use_vector=False)
    engine.initialize()
    engine.vector_engine = LocalVectorStore()
    engine.vector_engine.backend_type = 'local_tfidf'

    # Add test documents
    documents = [
        Document(f"Test document {i}: Content about {i}", {"source": "test.txt"})
        for i in range(100)
    ]
    engine.add_documents(documents)

    perf = PerformanceTest()

    # Test multiple searches
    queries = [
        "test",
        "document",
        "content",
        "testing",
        "automotive"
    ]

    print("\nRunning 5 search queries...")

    for query in queries:
        def search_query():
            return engine.search_similar(query, top_k=5)

        results, search_time = perf.measure_time(f"Search '{query}'", search_query)
        assert len(results) <= 5

    perf.print_summary()

    # Check average search time
    search_times = [r['time_ms'] for r in perf.results]
    avg_search = sum(search_times) / len(search_times)

    print(f"\nAverage search time: {avg_search:.2f} ms")

    if avg_search < 100:
        print("[OK] Excellent performance!")
    elif avg_search < 500:
        print("[OK] Good performance!")
    else:
        print("[WARN] Performance may need optimization")

    return True


def test_query_performance():
    """Test full query performance (with LLM)"""
    print("\n" + "=" * 60)
    print("Performance Test: Full Query (No LLM)")
    print("=" * 60)

    # Create and populate engine
    engine = EnhancedRAGEngine(use_vector=False)
    engine.initialize()
    engine.vector_engine = LocalVectorStore()
    engine.vector_engine.backend_type = 'local_tfidf'

    # Add test documents
    documents = [
        Document(f"Test document {i} with content", {"source": "test.txt"})
        for i in range(50)
    ]
    engine.add_documents(documents)

    perf = PerformanceTest()

    # Test queries
    queries = ["test", "content", "query"]

    print("\nRunning 3 queries...")

    for query in queries:
        def run_query():
            return engine.query_with_sources(query, use_llm=False)

        perf.measure_time(f"Query '{query}' (no LLM)", run_query)

    perf.print_summary()

    return True


def run_all_performance_tests():
    """Run all performance tests"""
    print("\n" + "=" * 70)
    print("Performance Test Suite")
    print("=" * 70)

    tests = [
        ("Initialization", test_initialization_performance),
        ("Add Documents", test_add_documents_performance),
        ("Search", test_search_performance),
        ("Query", test_query_performance)
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
    print("Performance Test Summary")
    print("=" * 70)
    print(f"Total: {len(tests)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\nAll performance tests PASSED!")
        return True
    else:
        print(f"\n{failed} test(s) FAILED")
        return False


if __name__ == "__main__":
    try:
        success = run_all_performance_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nPerformance test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
