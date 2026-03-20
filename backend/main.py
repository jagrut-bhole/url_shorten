from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlmodel import SQLModel
 
from core.config import settings
from db.database import engine
 
# Import routers
from api.auth import router as auth_router
from api.users import router as users_router

load_dotenv()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router,  prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

# Startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# Health check route
@app.get("/")
def root():
    return {"service": settings.APP_NAME}
 
@app.get("/health")
def health():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
