import sys
import os

# Add the parent directory to the Python import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from database.database import Database
from config.settings import Settings
from analysis.volume_tracker import VolumeTracker

from fastapi import FastAPI, Depends, HTTPException, Header

app = FastAPI()

# Simulated database of API keys
VALID_API_KEYS = {
    "user1": "key1",
    "user2": "key2",
}

def validate_api_key(api_key: str = Header(...)):
    if api_key not in VALID_API_KEYS.values():
        raise HTTPException(status_code=403, detail="Invalid API key")
@app.get("/")
def read_root():
    return {"message": "Welcome to the DEX API Gateway"}

@app.get("/volume")
async def get_volume(start_time: int, end_time: int, api_key: str = Depends(validate_api_key)):
    return {"message": f"Volume data for {start_time} to {end_time}"}

# Initialize database and VolumeTracker
db = Database(Settings.POSTGRES_CONFIG)
volume_tracker = VolumeTracker(db)
