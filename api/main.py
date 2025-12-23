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
from . import models, schemas
from .ai_service import GrokAIService
from .email_services import EmailTransactionParser, connect_gmail

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize Grok AI Service
ai_service = GrokAIService()

app = FastAPI(
    title="FinanceAI API",
    description="Backend for Insightful Finance AI - Powered by xAI Grok",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Routes
@app.get("/")
def root():
    return {"message": "FinanceAI API", "status": "running", "ai": "xAI Grok"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "ai_provider": "xAI Grok", "model": "grok-beta"}


# Authentication
@app.post("/api/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/api/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "name": user.name}
    }


# Dashboard Stats
@app.get("/api/dashboard/stats")
def get_dashboard_stats(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(abs(t.amount) for t in transactions if t.type == "expense")
    total_balance = total_income - total_expenses
    savings_rate = (total_balance / total_income * 100) if total_income > 0 else 0

    return {
        "total_balance": total_balance,
        "monthly_income": total_income,
        "monthly_expenses": total_expenses,
        "savings_rate": round(savings_rate, 1)
    }


# Transactions
@app.get("/api/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(
        skip: int = 0,
        limit: int = 50,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions


@app.post("/api/transactions", response_model=schemas.TransactionResponse)
def create_transaction(
        transaction: schemas.TransactionCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    new_transaction = models.Transaction(
        **transaction.dict(),
        user_id=current_user.id
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(
        transaction_id: int,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()

    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(db_transaction)
    db.commit()
    return {"message": "Transaction deleted"}


# Goals
@app.get("/api/goals", response_model=List[schemas.GoalResponse])
def get_goals(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    goals = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id
    ).all()
    return goals


@app.post("/api/goals", response_model=schemas.GoalResponse)
def create_goal(
        goal: schemas.GoalCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    new_goal = models.Goal(
        **goal.dict(),
        user_id=current_user.id
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


@app.delete("/api/goals/{goal_id}")
def delete_goal(
        goal_id: int,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()

    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(db_goal)
    db.commit()
    return {"message": "Goal deleted"}


# Analytics
@app.get("/api/analytics/spending")
def get_spending_analytics(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "expense"
    ).all()

    categories = {}
    for txn in transactions:
        category = txn.category
        categories[category] = categories.get(category, 0) + abs(txn.amount)

    spending_data = [
        {"name": cat, "value": amt} for cat, amt in categories.items()
    ]

    return {"data": spending_data, "total": sum(categories.values())}


# AI Advisor
@app.post("/api/ai/advice")
async def get_ai_advice(
        query: schemas.AIQuery,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Get user data
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).order_by(models.Transaction.date.desc()).limit(50).all()

    goals = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id
    ).all()

    # Get stats
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(abs(t.amount) for t in transactions if t.type == "expense")
    total_balance = total_income - total_expenses
    savings_rate = (total_balance / total_income * 100) if total_income > 0 else 0

    stats = {
        "total_balance": total_balance,
        "monthly_income": total_income,
        "monthly_expenses": total_expenses,
        "savings_rate": savings_rate
    }

    # Convert to dict
    transactions_dict = [
        {
            "title": t.title,
            "amount": t.amount,
            "category": t.category,
            "type": t.type
        } for t in transactions
    ]

    goals_dict = [
        {
            "title": g.title,
            "target": g.target,
            "current": g.current
        } for g in goals
    ]

    # Get AI advice
    advice = await ai_service.get_financial_advice(
        user_query=query.query,
        transactions=transactions_dict,
        goals=goals_dict,
        stats=stats
    )

    return {"advice": advice}


# Gmail/IMAP Integration
@app.post("/api/gmail/connect")
def connect_gmail(
        credentials: schemas.GmailCredentials,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        parser = EmailTransactionParser(credentials.email, credentials.app_password)
        parser.connect("imap.gmail.com")
        parser.disconnect()

        # Store encrypted credentials (implement encryption in production)
        current_user.gmail_email = credentials.email
        current_user.gmail_connected = True
        db.commit()

        return {"message": "Gmail connected successfully", "email": credentials.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/gmail/sync")
def sync_gmail_transactions(
        credentials: schemas.GmailCredentials,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        parser = EmailTransactionParser(credentials.email, credentials.app_password)
        parser.connect("imap.gmail.com")

        # Fetch transactions from emails
        email_transactions = parser.fetch_transactions(days=30)
        parser.disconnect()

        # Save to database
        new_count = 0
        for txn_data in email_transactions:
            # Check if transaction already exists
            existing = db.query(models.Transaction).filter(
                models.Transaction.user_id == current_user.id,
                models.Transaction.title == txn_data["title"],
                models.Transaction.amount == txn_data["amount"]
            ).first()

            if not existing:
                new_transaction = models.Transaction(
                    user_id=current_user.id,
                    title=txn_data["title"],
                    amount=txn_data["amount"],
                    type=txn_data["type"],
                    category=txn_data["category"],
                    bank=txn_data["bank"],
                    date=datetime.fromisoformat(txn_data["date"])
                )
                db.add(new_transaction)
                new_count += 1

        db.commit()

        return {
            "message": "Sync completed",
            "total_found": len(email_transactions),
            "new_transactions": new_count
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/gmail/status")
def gmail_status(
        current_user: models.User = Depends(get_current_user)
):
    return {
        "connected": current_user.gmail_connected,
        "email": current_user.gmail_email if current_user.gmail_connected else None
    }