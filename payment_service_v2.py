import uuid
from decimal import Decimal
from datetime import datetime
from models import Transaction
from sqlalchemy.orm import Session
from crypto_api import CoinGeckoAPI, BlockchainAPI, EtherscanAPI, CryptoAPIException
import logging
from config import ETHERSCAN_API_KEY

logger = logging.getLogger(__name__)

class PaymentServiceV2:
    """Enhanced payment service with real cryptocurrency API integration"""
    
    # Supported cryptocurrencies with their networks
    SUPPORTED_CRYPTOS = {
        'BTC': {
            'name': 'Bitcoin',
            'network': 'bitcoin',
            'decimals': 8,
        },
        'ETH': {
            'name': 'Ethereum',
            'network': 'ethereum',
            'decimals': 18,
        },
        'LTC': {
            'name': 'Litecoin',
            'network': 'litecoin',
            'decimals': 8,
        },
        'XRP': {
            'name': 'Ripple',
            'network': 'ripple',
            'decimals': 6,
        },
    }
    
    # Supported fiat currencies
    SUPPORTED_FIATS = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
    
    # Wallet validators with real blockchain integration
    WALLET_VALIDATORS = {
        'BTC': {
            'format': lambda x: x.startswith(('bc1', '1', '3')) and len(x) in [26, 34, 42],
            'api_validator': 'blockchain',
        },
        'ETH': {
            'format': lambda x: x.startswith('0x') and len(x) == 42,
            'api_validator': 'etherscan',
        },
        'LTC': {
            'format': lambda x: x.startswith(('L', 'M', '3')) and len(x) in [26, 34],
            'api_validator': 'blockchain',
        },
        'XRP': {
            'format': lambda x: x.startswith('r') and len(x) > 25,
            'api_validator': None,  # No public free API for XRP validation
        },
    }
    
    def __init__(self, session: Session, coingecko_cache_ttl: int = 60, etherscan_api_key: str = None):
        """Initialize enhanced payment service
        
        Args:
            session: SQLAlchemy database session
            coingecko_cache_ttl: Cache TTL for exchange rates (seconds)
            etherscan_api_key: Etherscan API key for Ethereum validation
        """
        self.session = session
        self.coingecko = CoinGeckoAPI(cache_ttl=coingecko_cache_ttl)
        self.blockchain = BlockchainAPI()
        self.etherscan = EtherscanAPI(api_key=etherscan_api_key or ETHERSCAN_API_KEY)
    
    def validate_wallet_address(self, crypto: str, wallet_address: str) -> bool:
        """Validate wallet address using real blockchain APIs
        
        Args:
            crypto: Cryptocurrency symbol
            wallet_address: Wallet address to validate
            
        Returns:
            bool: True if valid, raises exception if invalid
            
        Raises:
            ValueError: If validation fails
        """
        if crypto not in self.WALLET_VALIDATORS:
            raise ValueError(f"Unsupported cryptocurrency: {crypto}")
        
        validator_config = self.WALLET_VALIDATORS[crypto]
        
        # First, check format
        if not validator_config['format'](wallet_address):
            raise ValueError(f"Invalid {crypto} wallet address format: {wallet_address}")
        
        # Then validate with blockchain API if available
        api_validator = validator_config.get('api_validator')
        
        try:
            if api_validator == 'blockchain' and crypto == 'BTC':
                logger.info(f"Validating Bitcoin address: {wallet_address}")
                self.blockchain.validate_bitcoin_address(wallet_address)
                logger.info(f"Bitcoin address validated successfully")
                
            elif api_validator == 'etherscan' and crypto == 'ETH':
                logger.info(f"Validating Ethereum address: {wallet_address}")
                self.etherscan.validate_ethereum_address(wallet_address)
                logger.info(f"Ethereum address validated successfully")
                
        except CryptoAPIException as e:
            logger.warning(f"API validation warning: {str(e)}")
            # Continue anyway as some addresses may not have balance yet
        
        return True
    
    def create_purchase(self, crypto_symbol: str, fiat_symbol: str,
                       fiat_amount: float, wallet_address: str) -> Transaction:
        """Create a new purchase transaction with real exchange rates
        
        Args:
            crypto_symbol: Cryptocurrency symbol
            fiat_symbol: Fiat currency symbol
            fiat_amount: Amount in fiat currency
            wallet_address: Destination wallet address
            
        Returns:
            Transaction: Created transaction object
            
        Raises:
            ValueError: If validation fails
            CryptoAPIException: If API call fails
        """
        # Validate inputs
        crypto_symbol = crypto_symbol.upper()
        fiat_symbol = fiat_symbol.upper()
        
        if crypto_symbol not in self.SUPPORTED_CRYPTOS:
            raise ValueError(f"Unsupported cryptocurrency: {crypto_symbol}")
        
        if fiat_symbol not in self.SUPPORTED_FIATS:
            raise ValueError(f"Unsupported fiat currency: {fiat_symbol}")
        
        if fiat_amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Validate wallet address
        self.validate_wallet_address(crypto_symbol, wallet_address)
        
        # Get real-time exchange rate
        logger.info(f"Fetching exchange rate for {crypto_symbol}/{fiat_symbol}")
        try:
            exchange_rate = self.coingecko.get_exchange_rate(crypto_symbol, fiat_symbol)
        except CryptoAPIException as e:
            logger.error(f"Failed to get exchange rate: {str(e)}")
            raise ValueError(f"Failed to get exchange rate: {str(e)}")
        
        # Calculate crypto amount
        fiat_decimal = Decimal(str(fiat_amount))
        crypto_amount = fiat_decimal / exchange_rate
        
        # Round to appropriate decimal places
        decimals = self.SUPPORTED_CRYPTOS[crypto_symbol]['decimals']
        crypto_amount = crypto_amount.quantize(Decimal(10) ** -decimals)
        
        # Create transaction
        transaction = Transaction(
            id=str(uuid.uuid4()),
            crypto_symbol=crypto_symbol,
            fiat_symbol=fiat_symbol,
            fiat_amount=fiat_decimal,
            crypto_amount=crypto_amount,
            wallet_address=wallet_address,
            exchange_rate=exchange_rate,
            status='pending',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.session.add(transaction)
        self.session.commit()
        
        logger.info(f"Transaction created: {transaction.id}")
        return transaction
    
    def get_market_data(self, crypto: str, fiat: str) -> dict:
        """Get market data for a cryptocurrency
        
        Args:
            crypto: Cryptocurrency symbol
            fiat: Fiat currency symbol
            
        Returns:
            dict: Market data
        """
        try:
            return self.coingecko.get_market_data(crypto.upper(), fiat.upper())
        except CryptoAPIException as e:
            logger.error(f"Failed to get market data: {str(e)}")
            raise
    
    def get_transaction_status(self, transaction_id: str) -> Transaction:
        """Get transaction status
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction: Transaction object
        """
        transaction = self.session.query(Transaction).filter_by(id=transaction_id).first()
        
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        return transaction
    
    def get_all_transactions(self):
        """Get all transactions
        
        Returns:
            list: List of transactions
        """
        return self.session.query(Transaction).order_by(Transaction.created_at.desc()).all()
    
    def update_transaction_status(self, transaction_id: str, status: str):
        """Update transaction status
        
        Args:
            transaction_id: Transaction ID
            status: New status
            
        Returns:
            Transaction: Updated transaction
        """
        transaction = self.get_transaction_status(transaction_id)
        transaction.status = status
        transaction.updated_at = datetime.utcnow()
        self.session.commit()
        
        logger.info(f"Transaction {transaction_id} status updated to {status}")
        return transaction
