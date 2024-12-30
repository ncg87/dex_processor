from fastapi import FastAPI, Query
from typing import Optional
from database.database import Database
from config.settings import Settings
from analysis.volume_tracker import VolumeTracker

# Initialize FastAPI app
app = FastAPI()

# Initialize database and VolumeTracker
db = Database(Settings.POSTGRES_CONFIG)
volume_tracker = VolumeTracker(db)

@app.get("/")
def read_root():
    return {"message": "Welcome to the DEX API Gateway"}

@app.get("/volume")
def get_volume(
    start_time: int = Query(..., description="Start time in UNIX timestamp"),
    end_time: int = Query(..., description="End time in UNIX timestamp"),
    dex_id: Optional[str] = Query(None, description="Optional DEX identifier")
):
    """
    Fetch volume data for the specified time range and optional DEX.
    """
    try:
        volume_data = volume_tracker.get_volume_by_crypto(start_time, end_time, dex_id)
        return volume_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/transactions")
def get_transactions(
    start_time: int = Query(..., description="Start time in UNIX timestamp"),
    end_time: int = Query(..., description="End time in UNIX timestamp"),
    dex_id: Optional[str] = Query(None, description="Optional DEX identifier")
):
    """
    Fetch transaction data for the specified time range and optional DEX.
    """
    try:
        data = db.get_events_by_time("transactions", start_time, end_time, dex_id)
        return {"transactions": data}
    except Exception as e:
        return {"error": str(e)}
