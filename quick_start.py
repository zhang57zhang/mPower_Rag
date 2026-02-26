"""
Quick start - Use local TF-IDF vector store
Fast setup without external dependencies
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from simple_config import settings, Document
from simple_rag_engine import EnhancedRAGEngine
from local_vector_store import LocalVectorStore

def main():
    print("=" * 60)
    print("mPower_Rag - Quick Start (Local TF-IDF)")
    print("=" * 60)

    # Create RAG engine
    print("\n[1/3] Creating RAG engine...")
    engine = EnhancedRAGEngine(use_vector=False)
    engine.initialize()

    # Use local vector store
    print("[2/3] Initializing local TF-IDF vector store...")
    engine.vector_engine = LocalVectorStore()
    engine.vector_engine.backend_type = "local_tfidf"

    # Load documents from knowledge base
    print("[3/3] Loading documents from knowledge base...")
    knowledge_dir = settings.knowledge_base_dir

    doc_dicts = []
    documents = []

    for file_path in knowledge_dir.glob("*.txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split into chunks
            chunks = content.split("\n\n")
            for i, chunk in enumerate(chunks):
                chunk = chunk.strip()
                if len(chunk) > 50:
                    doc_dict = {
                        "id": f"{file_path.name}_{i}",
                        "content": chunk,
                        "source": file_path.name,
                        "metadata": {"source": file_path.name, "chunk_index": i}
                    }
                    doc_dicts.append(doc_dict)
                    documents.append(Document(chunk, doc_dict["metadata"]))

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    if not doc_dicts:
        print("No documents found in knowledge base")
        print("Adding sample documents...")
        doc_dicts = [
            {"id": "sample_0", "content": "Bluetooth testing includes device discovery, pairing and data transmission", "source": "sample.txt", "metadata": {}},
            {"id": "sample_1", "content": "ECU diagnosis reads fault codes from OBD interface", "source": "sample.txt", "metadata": {}},
            {"id": "sample_2", "content": "CAN bus testing verifies data frame integrity", "source": "sample.txt", "metadata": {}}
        ]
        documents = [
            Document(doc["content"], doc["metadata"]) for doc in doc_dicts
        ]

    # Add documents
    engine.vector_engine.add_documents(doc_dicts)
    engine.documents = documents

    print(f"Loaded {len(documents)} document chunks")

    # Save engine for API use
    print("\n" + "=" * 60)
    print("Initialization completed!")
    print("=" * 60)

    # Test search
    print("\nQuick test:")
    test_queries = ["bluetooth", "ECU", "CAN"]
    for query in test_queries:
        results = engine.search_similar(query, top_k=2)
        if results:
            print(f"  '{query}' -> Found {len(results)} results")
        else:
            print(f"  '{query}' -> No results")

    print("\nReady to start API server!")
    print("Run: python simple_api.py")

    # Note: In a real setup, you would save the engine to a file
    # or use a more sophisticated initialization in simple_api.py

if __name__ == "__main__":
    main()
