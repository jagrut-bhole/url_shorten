from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
from dotenv import load_dotenv

# Database Setup
from sqlmodel import SQLModel
from db import models
from db.database import engine

load_dotenv()

app = FastAPI(
    title="URL Shortener"
)

# Cors Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_db():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db()


@app.get('/')
def read_root():
    return {"service":"URL Shortener"}

@app.get('/health')
def read_health():
    return {"status":"OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=120,
    )


# Start the server with uvicorn main:app --reload