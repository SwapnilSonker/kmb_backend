import os
from fastapi import Depends, FastAPI, HTTPException, Header
from ollama import chat
from ollama import ChatResponse
from dotenv import load_dotenv

load_dotenv()
API_KEY_CREDITS = {os.getenv('API_CREDIT'): 2}


app = FastAPI()

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