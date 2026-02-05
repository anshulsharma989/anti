from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
from services.rag import search_documents

app = FastAPI(title="Student Knowledge Base API")

# Fix 405 Method Not Allowed / CORS Error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS)
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    model: str = "llama3" # Default model

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Knowledge Base API"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    RAG Endpoint:
    1. Search related documents in Supabase.
    2. Construct prompt with Context.
    3. Send to Ollama.
    """
    try:
        # 1. Retrieve Context
        context_results = search_documents(request.question, match_count=5)
        
        # Build Context String
        context_text = "\n\n".join([item['content'] for item in context_results])
        
        if not context_text:
            context_text = "No specific context found in the uploaded books."

        # 2. Construct Prompt
        system_prompt = f"""You are a helpful student tutor. 
        Answer the student's question based ONLY on the following context from their textbooks.
        If the answer is not in the context, say "I couldn't find the answer in your books."
        
        Context:
        {context_text}
        """

        # 3. Call Ollama (Local)
        # Ensure 'llama3' or the requested model is pulled locally: `ollama pull llama3`
        response = ollama.chat(model=request.model, messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': request.question},
        ])

        return {
            "answer": response['message']['content'],
            "sources": [item['metadata'] for item in context_results]
        }

    except Exception as e:
        # Graceful error handling if Ollama is not running or model missing
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
