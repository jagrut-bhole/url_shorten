from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session
from services.click_service import log_click

from datetime import datetime

from db.database import get_session
from core.config import settings
from db.database import engine
 
# Import routers
from api.auth import router as auth_router
from api.users import router as users_router
from api.url import router as url_router

# Cache setup
from helpers.urlHelper import get_url_from_cache_short_code

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
app.include_router(url_router, prefix="/api/v1")

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

@app.get("/{short_code}")
async def redirect(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db : Session = Depends(get_session)
):
    # Cache-first lookup: helper returns from Redis when available,
    # otherwise it falls back to DB and warms cache.
    url = get_url_from_cache_short_code(short_code, db)
    
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    
    if isinstance(url, dict):
        original_url = url["original_url"]
        expires_at = url.get("expires_at")
        url_id = url["id"]
    else:
        original_url = url.original_url
        expires_at = url.expires_at
        url_id = url.id
    
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        if expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="URL has expired")
    
    # Log the click WITHOUT blocking the redirect
    # BackgroundTasks runs AFTER the response is sent, so the user doesn't wait for DB logging
    
    background_tasks.add_task(log_click, url_id, request, db)
    
    return RedirectResponse(original_url, status_code=307)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
