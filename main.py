from database.database import Database
from config.settings import Settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def main():
    db = Database(Settings.POSTGRES_CONFIG)

if __name__ == "__main__":
    main()