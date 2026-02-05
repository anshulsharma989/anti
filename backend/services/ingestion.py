import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from .database import supabase

# Load a small, fast local embedding model
# all-mpnet-base-v2 is 768 dimensions (matches our DB) and higher quality than MiniLM
embedding_model = SentenceTransformer('all-mpnet-base-v2')

def extract_text_from_pdf(file_path_or_buffer):
    """
    Extracts text from a PDF file object or path.
    """
    reader = pypdf.PdfReader(file_path_or_buffer)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Splits text into chunks for better retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_text(text)
    return chunks

def generate_embeddings(chunks: list[str]):
    """
    Generates vector embeddings for a list of text chunks using local model.
    """
    embeddings = embedding_model.encode(chunks)
    return embeddings.tolist()

def store_document(filename: str, chunks: list[str], embeddings: list[list[float]]):
    """
    Stores chunks and embeddings in Supabase.
    """
    data = []
    for chunk, embedding in zip(chunks, embeddings):
        record = {
            "content": chunk,
            # 'metadata' field in DB is jsonb, so we can store arbitrary dicts
            "metadata": {"source": filename},
            "embedding": embedding
        }
        data.append(record)
    
    # Batch insert to avoid hitting limits or timeouts
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        supabase.table("document_chunks").insert(batch).execute()

def process_and_store_pdf(uploaded_file, filename: str):
    """
    Orchestrates the entire flow: Extract -> Chunk -> Embed -> Store
    """
    # 1. Extract
    text = extract_text_from_pdf(uploaded_file)
    
    # 2. Chunk
    chunks = split_text_into_chunks(text)
    
    # 3. Embed
    embeddings = generate_embeddings(chunks)
    
    # 4. Store
    store_document(filename, chunks, embeddings)
    
    return len(chunks)
