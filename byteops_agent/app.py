import asyncio
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="ByteOps Agent")

@app.get("/")
def home():
    return {"status": "ByteOps Agent running", "dashboard": "coming online"}

async def run():
    config = uvicorn.Config(app, host="127.0.0.1", port=8844, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
