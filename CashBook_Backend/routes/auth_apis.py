from fastapi import APIRouter, HTTPException
from models import User, LoginRequest
from core.database import conn_mongo_client
from passlib.context import CryptContext
from uuid import uuid4
from datetime import datetime


mongo_client = conn_mongo_client()
db = mongo_client["cashbook"]

routes = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:72].decode("utf-8", "ignore")
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:72].decode("utf-8", "ignore")
    return pwd_context.verify(truncated, hashed_password)

# ----------- User -----------
@routes.post("/register")
async def register_user(user: User):
    existing_user = db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists with this email")

    user_id = str(uuid4())
    hashed_pw = hash_password(user.password)

    user_dict = {
        "user_id": user_id,
        "user_name": user.user_name,
        "email": user.email,
        "password": hashed_pw,
        "created_at": datetime.now()
    }

    db.users.insert_one(user_dict)

    return {"message": "User registered successfully", "user_id": user_id}

@routes.post("/login")
async def login_user(request: LoginRequest):
    email = request.email
    password = request.password
    user = db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Optional: you can return a JWT token here for secure session
    return {
        "message": "Login successful",
        "user": {
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "email": user["email"]
        }
    }

@routes.get("/get-user/{user_id}")
async def get_user(user_id: str):
    user = db.users.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
