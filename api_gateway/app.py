import sys
import os

# Add the parent directory to the Python import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from database.database import Database
from config.settings import Settings
from analysis.volume_tracker import VolumeTracker

from fastapi import FastAPI, Depends, HTTPException, Header, Query

app = FastAPI()

# Simulated database of API keys
VALID_API_KEYS = {
    "user1": "key1",
    "user2": "key2",
}

def validate_api_key(api_key: str = Header(..., alias="api-key")):
    if api_key not in VALID_API_KEYS.values():
        raise HTTPException(status_code=403, detail="Invalid API key")

@app.get("/")
def read_root():
    return {"message": "Welcome to the DEX API Gateway"}

# Initialize database and VolumeTracker
db = Database(Settings.POSTGRES_CONFIG)
volume_tracker = VolumeTracker(db)

@app.get("/volume")
async def get_volume(start_time: int, end_time: int, dex_id: Optional[str] = Query(None, description="Optional DEX identifier"), api_key: str = Depends(validate_api_key)):
    """
    Fetch transaction data for the specified time range and optional DEX.
    """
    try:
        volume_data = volume_tracker.get_volume_by_crypto(start_time, end_time, dex_id)
        return volume_data
    except Exception as e:
        return {"error": str(e)}
