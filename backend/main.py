"""
FastAPI Server for Custom LLM Chat Interface
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import uvicorn

from llm_client import MemoryEnhancedLLMClient, format_messages_for_llm
from gptclient import OpenAIMessage
from data_tools import data_analyzer
from memory_client import MemoryClient


# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-4o-mini"
    max_tokens: int = 1000
    temperature: float = 0.7


class ChatResponse(BaseModel):
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    model: str


# Initialize FastAPI app
app = FastAPI(
    title="Custom LLM API",
    description="Backend API for custom LLM chat interface",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://localhost:5174", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm_client = MemoryEnhancedLLMClient()
memory_client = MemoryClient()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Custom LLM API is running", "status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    OpenAI-compatible chat completion endpoint
    
    Args:
        request: Chat completion request with messages
        
    Returns:
        Chat completion response
    """
    try:
        # Convert Pydantic models to OpenAIMessage objects
        messages = [
            OpenAIMessage(role=msg.role, content=msg.content)
            for msg in request.messages
        ]
        
        # Get response from LLM client
        response = await llm_client.get_response(messages)
        
        # Return response in OpenAI format
        return ChatResponse(
            choices=response.choices,
            usage=response.usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            model=request.model
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/api/models")
async def list_models():
    """List available models"""
    return {
        "data": [
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai"
            }
        ]
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and analyze data files (CSV, JSON, Excel)
    
    Args:
        file: Uploaded file
        
    Returns:
        File analysis results
    """
    try:
        # Check file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        # Check file type
        allowed_extensions = {'.csv', '.json', '.xlsx', '.xls'}
        file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Load and analyze file
        result = data_analyzer.load_file(file_content, file.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Store file information in memory
        memory_client.add_file_data(file.filename, result)
        
        # Add chart suggestions
        suggestions = data_analyzer.get_chart_suggestions()
        result["chart_suggestions"] = suggestions
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/data/info")
async def get_data_info():
    """Get information about currently loaded data"""
    if data_analyzer.data is None:
        return {"loaded": False, "message": "No data currently loaded"}
    
    return {
        "loaded": True,
        "shape": data_analyzer.data.shape,
        "columns": list(data_analyzer.data.columns),
        "summary": data_analyzer.data_info
    }


@app.post("/api/data/query")
async def query_data(request: dict):
    """Query the loaded data"""
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    result = data_analyzer.query_data(query)
    return result


@app.post("/api/data/visualize")
async def create_visualization(request: dict):
    """Create data visualization"""
    chart_type = request.get("chart_type", "")
    params = request.get("params", {})
    
    if not chart_type:
        raise HTTPException(status_code=400, detail="chart_type parameter is required")
    
    result = data_analyzer.create_visualization(chart_type, **params)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get memory system statistics"""
    return memory_client.get_memory_stats()


@app.post("/api/memory/search")
async def search_memory(request: dict):
    """Search memory for relevant content"""
    query = request.get("query", "")
    k = request.get("k", 5)
    min_similarity = request.get("min_similarity", 0.3)
    
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    results = memory_client.search_memories(query, k, min_similarity)
    
    return {
        "query": query,
        "results": [
            {
                "content": memory.content,
                "entry_type": memory.entry_type,
                "similarity": float(similarity),
                "timestamp": memory.timestamp.isoformat(),
                "metadata": memory.metadata
            }
            for memory, similarity in results
        ]
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check with memory system status"""
    memory_stats = memory_client.get_memory_stats()
    
    return {
        "status": "healthy",
        "service": "custom-llm-api",
        "version": "1.0.0",
        "data_loaded": data_analyzer.data is not None,
        "memory_system": {
            "total_memories": memory_stats.get("total_memories", 0),
            "memory_types": memory_stats.get("entry_types", {}),
            "status": "active"
        },
        "endpoints": {
            "chat": "/api/chat",
            "upload": "/api/upload",
            "data_info": "/api/data/info",
            "data_query": "/api/data/query",
            "visualize": "/api/data/visualize",
            "memory_stats": "/api/memory/stats",
            "memory_search": "/api/memory/search",
            "models": "/api/models",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    print("Starting Custom LLM API server...")
    print("API Documentation available at: http://localhost:8000/docs")
    print("Health check available at: http://localhost:8000/api/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
