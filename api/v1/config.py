# /api/v1/config.py

import os
# deprecated due to containerization
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

## values are now passed from docker-compose

CONFIG = {
    'MONGO_URL': os.getenv('MONGO_URL'),
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
    'RAPID_MUT_FUND_KEY': os.getenv('RAPID_MUT_FUND_KEY'),
    'RAPID_URL': os.getenv('RAPID_URL'),
}
