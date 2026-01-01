import chromadb
from ..config import CHROMA_DIR
from .embeddings import get_model

client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_or_create_collection(
    name="personal_memory",
    metadata={"hnsw:space": "cosine"},
)

def add_memory(txt: str):
    """Store memory"""
    # Don't store questions
    if txt.strip().endswith("?") or len(txt.strip()) < 3:
        return
    
    # Generate embedding
    vector = get_model().embed_query(txt)
    
    # Create unique ID
    import hashlib
    memory_id = hashlib.md5(txt.encode()).hexdigest()[:16]
    
    # Always add (don't check for duplicates)
    collection.add(
        documents=[txt],
        embeddings=[vector],
        ids=[memory_id]
    )
    print(f"✓ Stored memory: '{txt}'")

def search_memory(query: str, k=5):
    """Search memories"""
    print(f"🔍 Searching for: '{query}'")
    
    vector = get_model().embed_query(query)
    
    # Get all memories first
    all_memories = collection.get()
    
    if all_memories['documents']:
        print("Found all memories")
    
    # Query
    results = collection.query(
        query_embeddings=[vector],
        n_results=k
    )
    
    # Simple filtering - just remove empty results
    if results["documents"] and results["documents"][0]:
        # Remove duplicates
        unique_docs = []
        seen = set()
        for doc in results["documents"][0]:
            if doc not in seen:
                unique_docs.append(doc)
                seen.add(doc)
        
        results["documents"] = [unique_docs]
    
    return results

def delete_memory_by_text(text: str):
    """Delete memory entries that exactly match text"""
    all_memories = collection.get()


    ids_to_delete = []
    for doc, mem_id in zip(all_memories["documents"], all_memories["ids"]):
        if doc.strip().lower() == text.strip().lower():
            ids_to_delete.append(mem_id)

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        print(f"🗑️ Deleted memory: '{text}'")
        return True

    return False
