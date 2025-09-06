from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
from typing import List, Dict, Optional

app = FastAPI(title="Smart Chat Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'llama2')

# Global model state
current_model = DEFAULT_MODEL

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []

class ModelRequest(BaseModel):
    model: str

class ChatResponse(BaseModel):
    response: str
    model: str

@app.get("/")
async def root():
    return {"message": "Smart Chat Backend is running!"}

@app.get("/health")
async def health_check():
    try:
        # Check if Ollama is reachable
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_status = "healthy" if response.status_code == 200 else "unhealthy"
        return {
            "status": "healthy",
            "ollama_status": ollama_status,
            "current_model": current_model
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/models")
async def get_models():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            models = [model["name"] for model in models_data.get("models", [])]
            return {"models": models}
        else:
            raise HTTPException(status_code=500, detail="Could not fetch models from Ollama")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama connection error: {str(e)}")

@app.post("/set_model")
async def set_model(request: ModelRequest):
    global current_model
    current_model = request.model
    return {"message": f"Model set to {current_model}"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Prepare the context from history
        context = ""
        for msg in request.history[-10:]:  # Keep last 10 messages for context
            role = "Human" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        # Prepare the prompt
        full_prompt = f"{context}Human: {request.message}\nAssistant:"
        
        # Call Ollama API
        ollama_request = {
            "model": current_model,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=ollama_request,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return ChatResponse(
                response=result["response"].strip(),
                model=current_model
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Ollama API error: {response.status_code}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)