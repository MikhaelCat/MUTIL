from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.core.config import settings
from app.api.routes import api_router
from app.core.database import Base, engine

# Создание таблиц в БД 
Base.metadata.create_all(bind=engine)

# FastAPI приложение
fastapi_app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/api/openapi.json",
    docs_url=f"/api/docs",
    redoc_url=f"/api/redoc"
)

# CORS middleware 
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
if os.path.exists(settings.MEDIA_ROOT):
    fastapi_app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")

fastapi_app.include_router(api_router, prefix="/api")

@fastapi_app.get("/")
async def root():
    return {"message": "Welcome to MUTIL API"}

# Flask приложение
from app.flask_app import create_flask_app
flask_app = create_flask_app()

# Настройка шаблонов для Flask
from flask import render_template
flask_app.template_folder = 'app/flask_app/templates'
flask_app.static_folder = 'app/flask_app/static'  

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)