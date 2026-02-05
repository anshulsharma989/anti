from sentence_transformers import SentenceTransformer
from .database import supabase

# Re-use the same model ensuring consistency
embedding_model = SentenceTransformer('all-mpnet-base-v2')

def search_documents(query: str, match_count: int = 5):
    """
    Searches Supabase for relevant content using the query.
    """
    # 1. Generate embedding for user query
    query_embedding = embedding_model.encode(query).tolist()
    
    # 2. Call Supabase RPC function (Postgres function)
    # The 'match_documents' function was defined in setup_db.sql
    response = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_threshold": 0.5, # Adjust based on quality needs
        "match_count": match_count
    }).execute()
    
    return response.data
