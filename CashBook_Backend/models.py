from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    user_id: Optional[str] = None
    user_name: str = ""
    password: str
    email: EmailStr = ""
    created_at: Optional[datetime] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Book(BaseModel):
    user_id: str
    book_id: Optional[str] = None
    book_name: str
    total_cash_in: Optional[float] = 0
    total_cash_out: Optional[float] = 0
    # transactions: List[Transaction] = Field(default_factory=list)

class Transaction(BaseModel):
    update_by: str
    book_id: str = None
    transaction_id: Optional[str] = None
    balance: Optional[float] = 0
    transaction_amount: float
    transaction_type: str
    remark: Optional[str] = ""
    category: Optional[str] = ""
    mode: Optional[str] = ""
    timestamp: Optional[datetime] = None
    date: Optional[str] = None
    time: Optional[str] = None

    #"Date","Time","Remark","Entry by","Mode","Cash In","Cash Out","Balance"