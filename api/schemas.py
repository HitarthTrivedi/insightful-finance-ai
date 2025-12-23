from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionCreate(BaseModel):
    title: str
    category: str
    amount: float
    date: Optional[datetime] = None
    type: str  # "income" or "expense"
    bank: Optional[str] = None
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    title: str
    category: str
    amount: float
    date: datetime
    type: str
    bank: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Goal Schemas
class GoalCreate(BaseModel):
    title: str
    target: float
    current: Optional[float] = 0.0
    deadline: Optional[datetime] = None
    color: Optional[str] = "primary"


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target: Optional[float] = None
    current: Optional[float] = None
    deadline: Optional[datetime] = None
    color: Optional[str] = None


class GoalResponse(BaseModel):
    id: int
    title: str
    target: float
    current: float
    deadline: Optional[datetime]
    color: str
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_balance: float
    monthly_income: float
    monthly_expenses: float
    savings_rate: float


class SpendingCategory(BaseModel):
    name: str
    value: float


# AI Schemas
class AIQuestion(BaseModel):
    question: str


# Gmail Schemas
class GmailConnect(BaseModel):
    email: str
    access_token: str


class GmailStatus(BaseModel):
    connected: bool
    email: Optional[str] = None
    last_synced: Optional[datetime] = None
    transactions_found: Optional[int] = None
class GmailCredentials(BaseModel):
    email: str
    app_password: str

class AIQuery(BaseModel):
    query: str