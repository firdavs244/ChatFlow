"""
ChatFlow - API Routers
"""

from fastapi import APIRouter

from app.routers import auth, users, chats, messages, files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(chats.router, prefix="/chats", tags=["Chats"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])

