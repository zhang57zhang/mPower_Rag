"""Quick Chinese query test"""
from simple_config import settings, Document
from simple_rag_engine import EnhancedRAGEngine
from local_vector_store import LocalVectorStore

engine = EnhancedRAGEngine(use_vector=False)
engine.initialize()
engine.vector_engine = LocalVectorStore()
engine.vector_engine.backend_type = 'local_tfidf'

knowledge_dir = settings.knowledge_base_dir
doc_dicts = []
documents = []

if knowledge_dir.exists():
    for file_path in knowledge_dir.glob('*.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks = content.split('\n\n')
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) > 50:
                doc_dict = {
                    'id': f'{file_path.stem}_{i}',
                    'content': chunk,
                    'source': file_path.name,
                    'metadata': {'source': file_path.name}
                }
                doc_dicts.append(doc_dict)
                documents.append(Document(chunk, doc_dict['metadata']))

print(f'Loaded {len(doc_dicts)} documents')
engine.vector_engine.add_documents(doc_dicts)
engine.documents = documents

# Test with Chinese queries
test_queries = ['蓝牙', 'ECU', '测试', '诊断', '流程']
print('\nTesting Chinese queries:')
for query in test_queries:
    results = engine.search_similar(query, top_k=2)
    print(f'\nQuery: {query} -> {len(results)} results')
    if results:
        for r in results:
            content = r['content'][:60] + '...' if len(r['content']) > 60 else r['content']
            print(f'  [{r["score"]:.3f}] {content}')
