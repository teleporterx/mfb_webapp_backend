# /api/v1/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

CONFIG = {
    'MONGO_URL': os.getenv('MONGO_URL'),
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY')
}
