import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("API_KEY", "fe_oa_7195db37233bd89a329e029f5cbab1cd2626d78db89982ba")
API_URL = "https://api.freemodel.dev/v1/chat/completions"

class ChatRequest(BaseModel):
    messages: list
    model: str = "gpt-3.5-turbo"

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": request.model,
                    "messages": request.messages,
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            data = response.json()
            return {"content": data["choices"][0]["message"]["content"]}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "ok", "message": "Freemodel proxy is running"}

@app.get("/health")
def health():
    return {"status": "alive"}
