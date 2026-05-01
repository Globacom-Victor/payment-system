import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/crypto_payment'
)

# API Configuration
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', 'YourEtherscanAPIKey')
COINGECKO_CACHE_TTL = int(os.getenv('COINGECKO_CACHE_TTL', '60'))

# Application Configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
