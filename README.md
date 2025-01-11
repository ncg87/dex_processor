# DEX Transaction Tracker System

A robust data pipeline system for tracking and analyzing transactions across multiple Decentralized Exchanges (DEXes). Currently supports Uniswap V2, Uniswap V3, Aerodrome, and Quickswap V3.

## Features

- Real-time transaction tracking across multiple DEXes
- Support for various transaction types (swaps, mints, burns, etc.)
- Automated data pipeline with configurable intervals
- Token metadata tracking and management
- PostgreSQL database with optimized partitioning
- RESTful API endpoints for data access
- Comprehensive volume analysis tools
- Concurrent processing of multiple DEX pipelines

## System Architecture

- **Database Layer**: PostgreSQL with optimized partitioning for time-series data
- **API Gateway**: FastAPI-based REST API with authentication
- **Data Pipelines**: Modular pipeline system for each supported DEX
- **Analysis Tools**: Volume tracking and token analysis capabilities

## Supported DEXes

- Uniswap V3
- Uniswap V2
- Aerodrome
- Quickswap V3

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dex-tracker-system.git
cd dex-tracker-system
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
DEXES=uniswap_v3,uniswap_v2,aerodrome,quickswap_v3
QUERY_INTERVAL=300
MAX_CONCURRENT_QUERIES=3
API_KEY=your_thegraph_api_key
```

4. Initialize the database:
```bash
python main.py
```

5. Start the data pipeline:
```bash
python run.py
```

6. Start the API server:
```bash
cd api_gateway
gunicorn app:app --config gunicorn_config.py
```

## API Endpoints

- `GET /dex_volume`: Get trading volume data by cryptocurrency
- `GET /token_metadata`: Retrieve token information
- `GET /crypto_volume`: Get trading volume data by DEX

All endpoints require API key authentication via the `api-key` header.

## Database Schema

The system uses a partitioned PostgreSQL database with tables for:
- Swaps
- Mints
- Burns
- Token metadata

Each table is partitioned by timestamp for optimal query performance.

## Dependencies

- Python 3.8+
- PostgreSQL 12+
- FastAPI
- SQLAlchemy
- requests
- python-dotenv

## Deployment

The system is designed to be deployed on AWS with:
- Application server on EC2
- Database on RDS
- NGINX as reverse proxy

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.