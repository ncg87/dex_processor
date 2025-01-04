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

@app.get("/dex_volume")
async def get_dex_volume(
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
        logger.info(f"Volume data retrieved successfully for {dex_id} from {start_time} to {end_time}")
        return volume_data
    except Exception as e:
        logger.error(f"Error fetching volume data: {str(e)}", exc_info=True)
        return {"error": str(e)}

@app.get("/token_metadata")
def get_token_metadata(token_id: Optional[str] = None, symbol: Optional[str] = None, name: Optional[str] = None, api_key: str = Depends(validate_api_key)):
    """
    Retrieve token data by symbol or token ID.
    """
    try:
        if token_id:
            tokens = db.get_token_by_id(token_id)
        elif symbol:
            tokens = db.get_tokens_by_symbol(symbol)
        else:
            tokens = db.get_all_tokens()
        return tokens
    except Exception as e:
        logger.error(f"Error fetching tokens: {str(e)}", exc_info=True)
        return {"error": str(e)}

@app.get("/crypto_volume")
def get_crypto_volume(
    start_time: int,
    end_time: int,
    crypto_id: Optional[str] = Query(None, description="ID of the cryptocurrency"),
    api_key: str = Depends(validate_api_key)
):
    """
    Fetch the volume of a specific cryptocurrency on all DEXs in the last 24 hours.
    Args:
        crypto_id: The ID of the cryptocurrency.
    Returns:
        JSON response containing the volumes by DEX.
    """
    try:
        volume_data = volume_tracker.get_volume_by_dex(start_time, end_time, crypto_id)
        logger.info(f"Volume data retrieved successfully for {crypto_id} from {start_time} to {end_time}")
        return volume_data
    except Exception as e:
        logger.error(f"Error fetching crypto volume: {str(e)}", exc_info=True)
        return {"error": str(e)}



