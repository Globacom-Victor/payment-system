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

# Email Configuration
SMTP_CONFIG = {
    'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', '587')),
    'email': os.getenv('SMTP_EMAIL', 'your_email@gmail.com'),
    'password': os.getenv('SMTP_PASSWORD', 'your_app_password'),
    'use_tls': os.getenv('SMTP_USE_TLS', 'True').lower() == 'true',
    'name': os.getenv('SMTP_NAME', 'Crypto Payment System'),
}

# Notification Configuration
NOTIFICATIONS_ENABLED = os.getenv('NOTIFICATIONS_ENABLED', 'True').lower() == 'true'
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
NOTIFY_CUSTOMER = os.getenv('NOTIFY_CUSTOMER', 'True').lower() == 'true'
NOTIFY_ADMIN = os.getenv('NOTIFY_ADMIN', 'True').lower() == 'true'

# Application Configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
