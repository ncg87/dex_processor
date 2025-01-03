import sys
import os

# Add the parent directory to the Python import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional
from database.database import Database
from config.settings import Settings
from analysis.volume_tracker import VolumeTracker
import logging

from fastapi import FastAPI, Depends, HTTPException, Header, Query

# Configure logging
logging.basicConfig(
    filename="api_gateway.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Simulated database of API keys
VALID_API_KEYS = {
    "user1": "key1",
    "user2": "key2",
}

def validate_api_key(api_key: str = Header(..., alias="api-key")):
    logger.info(f"Validating API key: {api_key}")
    if api_key not in VALID_API_KEYS.values():
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")
    logger.info(f"API key validated successfully: {api_key}")

@app.get("/")
def read_root():
    logger.info("Received request for root endpoint.")
    return {"message": "Welcome to the DEX API Gateway"}

# Initialize database and VolumeTracker
db = Database(Settings.POSTGRES_CONFIG)
volume_tracker = VolumeTracker(db)

@app.get("/volume")
async def get_volume(
    start_time: int,
    end_time: int,
    dex_id: Optional[str] = Query(None, description="Optional DEX identifier"),
    api_key: str = Depends(validate_api_key)
):
    """
    Fetch transaction data for the specified time range and optional DEX.
    """
    logger.info(f"Request for volume: start_time={start_time}, end_time={end_time}, dex_id={dex_id}")
    try:
        volume_data = volume_tracker.get_volume_by_crypto(start_time, end_time, dex_id)
        logger.info(f"Volume data retrieved successfully: {volume_data}")
        return volume_data
    except Exception as e:
        logger.error(f"Error fetching volume data: {str(e)}", exc_info=True)
        return {"error": str(e)}

@app.get("/tokens")
def get_tokens(symbol: Optional[str] = None, api_key: str = Depends(validate_api_key)):
    """
    Retrieve all token data or filter by symbol.
    """
    logger.info(f"Request for tokens: symbol={symbol}")
    try:
        if symbol:
            tokens = db.get_tokens_by_symbol(symbol)
        else:
            tokens = db.get_all_tokens()
        logger.info(f"Tokens retrieved successfully: {tokens}")
        return {"tokens": tokens}
    except Exception as e:
        logger.error(f"Error fetching tokens: {str(e)}", exc_info=True)
        return {"error": str(e)}


