import os
import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Header
from ollama import chat
from ollama import ChatResponse
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from typing import Dict, List

load_dotenv()
API_KEY_CREDITS = {os.getenv('API_CREDIT'): 2}


app = FastAPI()
fake_db : Dict[str, Dict] = {}

def verify_credits(api_key_credits: str = Header(None)):
    credits = API_KEY_CREDITS.get(api_key_credits, 0)
    if credits <= 0:
        raise HTTPException(status_code=403, detail="Not enough credits")
    return api_key_credits
    
    
@app.post('/generate')
def generate(prompt: str, api_key_credits: str = Depends(verify_credits)):
    API_KEY_CREDITS[api_key_credits] -= 1
    response : ChatResponse = chat(model = "llama3.2:latest", messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    return {"response": response["message"]["content"]}

class UserCreate(BaseModel):
    name: str
    email : EmailStr
    password: str
    
class UserResponse(BaseModel):
    name: str
    email: EmailStr    
    

async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pswd = bcrypt.hashpw(password.encode('utf-8'),salt).decode('utf-8')
    return pswd
    

@app.post("/register")
async def register(user : UserCreate):
    if user.email in fake_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    
    fake_db[user.email] = {
        "name": user.name,
        "email" : user.email,
        "password": hashed_password
    }
    
    return UserResponse(name = user.name, email = user.email)

@app.get("/users", response_model=List[UserResponse])
async def get_all_users():
    users = [UserResponse(name= data["name"], email= email) for email , data in fake_db.items()]
    return users
    
    