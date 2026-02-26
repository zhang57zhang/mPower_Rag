"""
Simple vector search test
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from simple_config import Document
from simple_rag_engine import EnhancedRAGEngine

def main():
    print("=" * 60)
    print("Vector Search Test")
    print("=" * 60)

    # Initialize engine
    print("\n[1/4] Initializing RAG engine...")
    engine = EnhancedRAGEngine(use_vector=True)
    success = engine.initialize()

    if not success:
        print("Failed to initialize RAG engine")
        return

    print("RAG engine initialized successfully")

    # Check backend
    print("\n[2/4] Checking vector engine backend...")
    if engine.vector_engine:
        backend = engine.vector_engine.backend_type
        print(f"Vector engine type: {backend}")

        if backend == "qdrant":
            print("Using Qdrant vector database")
        elif backend == "sentence_transformers":
            print("Using sentence-transformers (memory)")
        else:
            print("Using local TF-IDF vector storage")
    else:
        print("Vector engine not initialized")
        return

    # Add test documents
    print("\n[3/4] Adding test documents...")

    test_documents = [
        Document(
            "Bluetooth testing is important for automotive communication. Test steps include device discovery, pairing, connection verification and data transmission testing.",
            metadata={"source": "bluetooth_test.txt"}
        ),
        Document(
            "ECU diagnosis reads vehicle fault codes and real-time data through OBD interface. Common protocols include ISO 15765, KWP2000 and UDS.",
            metadata={"source": "ecu_diagnosis.txt"}
        ),
        Document(
            "CAN bus testing needs to verify data frame integrity, timing and load rate. Tools include Vector CANoe and CANalyzer.",
            metadata={"source": "can_bus_test.txt"}
        ),
        Document(
            "Vehicle software testing includes unit testing, integration testing and system testing. Automated testing frameworks can significantly improve testing efficiency.",
            metadata={"source": "software_test.txt"}
        )
    ]

    print(f"Adding {len(test_documents)} test documents...")
    engine.add_documents(test_documents)
    print("Test documents added successfully")

    # Test search
    print("\n[4/4] Testing search...")
    test_queries = ["bluetooth", "ECU", "CAN", "test"]

    for query in test_queries:
        results = engine.search_similar(query, top_k=2)

        print(f"\nQuery: '{query}'")
        if results:
            for i, result in enumerate(results):
                content = result['content'][:60] + "..." if len(result['content']) > 60 else result['content']
                method = "vector" if result.get("method") == "vector" else "keyword"
                print(f"  {i+1}. [{method}] [{result['score']:.3f}] {content}")
        else:
            print("  No results found")

    # Health check
    print("\n" + "=" * 60)
    print("Health Check")
    print("=" * 60)

    health = engine.health_check()
    print(f"Status: {health['status']}")
    print(f"Vector search: {health['vector_search']}")
    print(f"Document count: {health['document_count']}")
    if health.get('vector_info'):
        print(f"Vector info: {health['vector_info']}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
