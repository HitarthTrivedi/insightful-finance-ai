from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from passlib.context import CryptContext
import os

from .database import get_db, engine
from . import models
from . import schemas
from .ai_service import AIAdvisorService

# Initialize AI Service with Grok (Llama 3.3 70B)
ai_service = AIAdvisorService(provider="xai")

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinanceAI API", version="1.0.0")

# CORS Configuration - ALLOW YOUR VERCEL FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",  # Your Vercel frontend
        "https://your-custom-domain.com"  # Add your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# ... rest of the code remains the same ...