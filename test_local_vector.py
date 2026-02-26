"""
Quick test using local TF-IDF vector store
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from simple_config import Document
from simple_rag_engine import EnhancedRAGEngine
from local_vector_store import LocalVectorStore

print("=" * 60)
print("Local TF-IDF Vector Search Test")
print("=" * 60)

# Create engine with local vector store
print("\nCreating RAG engine with local TF-IDF...")
engine = EnhancedRAGEngine(use_vector=False)
engine.initialize()

# Initialize local vector store
print("Initializing local TF-IDF vector store...")
engine.vector_engine = LocalVectorStore()
engine.vector_engine.backend_type = "local_tfidf"

# Add test documents
print("\nAdding test documents...")
test_documents = [
    Document(
        "Bluetooth testing includes device discovery, pairing and data transmission verification",
        metadata={"source": "bluetooth_test.txt"}
    ),
    Document(
        "ECU diagnosis reads fault codes from OBD interface using UDS protocol",
        metadata={"source": "ecu_diagnosis.txt"}
    ),
    Document(
        "CAN bus testing verifies data frame integrity and timing with CANoe tool",
        metadata={"source": "can_bus_test.txt"}
    ),
    Document(
        "Software testing includes unit tests, integration tests and system tests",
        metadata={"source": "software_test.txt"}
    )
]

# Use local store to add documents
doc_dicts = []
for i, doc in enumerate(test_documents):
    doc_dicts.append({
        "id": i,
        "content": doc.page_content,
        "source": doc.metadata.get("source", ""),
        "metadata": doc.metadata
    })

engine.vector_engine.add_documents(doc_dicts)
engine.documents = test_documents

print(f"Added {len(test_documents)} documents")

# Test search
print("\nTesting search...")
test_queries = [
    ("bluetooth", "Bluetooth test"),
    ("ECU", "ECU diagnosis"),
    ("CAN", "CAN bus testing"),
    ("test", "software testing")
]

for query_en, query_desc in test_queries:
    print(f"\nQuery: '{query_desc}'")
    results = engine.vector_engine.search(query_en, top_k=2, score_threshold=0.05)

    if results:
        for i, result in enumerate(results):
            content = result['content'][:60] + "..." if len(result['content']) > 60 else result['content']
            print(f"  {i+1}. [{result['score']:.3f}] {content}")
            print(f"     Source: {result['source']}")
    else:
        print("  No results found")

# Health check
print("\n" + "=" * 60)
print("Health Check")
print("=" * 60)

info = engine.vector_engine.get_info()
print(f"Document count: {info['document_count']}")
print(f"Vector count: {info['vector_count']}")
print(f"Vocabulary size: {info['vocabulary_size']}")
print(f"Storage type: {info['storage_type']}")

print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)
