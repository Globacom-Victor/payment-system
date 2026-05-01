import requests
from decimal import Decimal
from typing import Dict, Tuple
import logging
from cachetools import TTLCache
import time

logger = logging.getLogger(__name__)

class CryptoAPIException(Exception):
    """Custom exception for API errors"""
    pass

class CoinGeckoAPI:
    """CoinGecko API client for real-time exchange rates"""
    
    BASE_URL = 'https://api.coingecko.com/api/v3'
    
    # Cryptocurrency ID mapping
    CRYPTO_IDS = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'LTC': 'litecoin',
        'XRP': 'ripple',
        'USDC': 'usd-coin',
        'USDT': 'tether',
    }
    
    # Fiat currency mapping
    FIAT_IDS = {
        'USD': 'usd',
        'EUR': 'eur',
        'GBP': 'gbp',
        'JPY': 'jpy',
        'CAD': 'cad',
        'AUD': 'aud',
    }
    
    def __init__(self, cache_ttl: int = 60):
        """Initialize CoinGecko API client
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 60)
        """
        self.cache = TTLCache(maxsize=100, ttl=cache_ttl)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoPaymentSystem/1.0'
        })
    
    def get_exchange_rate(self, crypto: str, fiat: str) -> Decimal:
        """Get current exchange rate from CoinGecko
        
        Args:
            crypto: Cryptocurrency symbol (e.g., 'BTC')
            fiat: Fiat currency symbol (e.g., 'USD')
            
        Returns:
            Decimal: Exchange rate
            
        Raises:
            CryptoAPIException: If API call fails
        """
        cache_key = f"{crypto}_{fiat}"
        
        # Check cache first
        if cache_key in self.cache:
            logger.info(f"Using cached rate for {cache_key}")
            return self.cache[cache_key]
        
        if crypto not in self.CRYPTO_IDS:
            raise CryptoAPIException(f"Unsupported cryptocurrency: {crypto}")
        if fiat not in self.FIAT_IDS:
            raise CryptoAPIException(f"Unsupported fiat currency: {fiat}")
        
        try:
            crypto_id = self.CRYPTO_IDS[crypto]
            fiat_id = self.FIAT_IDS[fiat]
            
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': fiat_id,
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rate = Decimal(str(data[crypto_id][fiat_id]))
            
            # Cache the result
            self.cache[cache_key] = rate
            logger.info(f"Exchange rate {crypto}/{fiat}: {rate}")
            
            return rate
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API error: {str(e)}")
            raise CryptoAPIException(f"Failed to get exchange rate: {str(e)}")
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response from CoinGecko: {str(e)}")
            raise CryptoAPIException(f"Invalid API response: {str(e)}")
    
    def get_market_data(self, crypto: str, fiat: str) -> Dict:
        """Get detailed market data for a cryptocurrency
        
        Args:
            crypto: Cryptocurrency symbol
            fiat: Fiat currency symbol
            
        Returns:
            Dict: Market data including price, market cap, volume
        """
        if crypto not in self.CRYPTO_IDS:
            raise CryptoAPIException(f"Unsupported cryptocurrency: {crypto}")
        if fiat not in self.FIAT_IDS:
            raise CryptoAPIException(f"Unsupported fiat currency: {fiat}")
        
        try:
            crypto_id = self.CRYPTO_IDS[crypto]
            fiat_id = self.FIAT_IDS[fiat]
            
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': fiat_id,
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()[crypto_id]
            
            return {
                'price': Decimal(str(data[fiat_id])),
                'market_cap': data.get(f'{fiat_id}_market_cap'),
                'volume_24h': data.get(f'{fiat_id}_24h_vol'),
                'change_24h': data.get(f'{fiat_id}_24h_change'),
            }
            
        except Exception as e:
            logger.error(f"Failed to get market data: {str(e)}")
            raise CryptoAPIException(f"Failed to get market data: {str(e)}")


class BlockchainAPI:
    """Blockchain.com API client for wallet validation and transaction monitoring"""
    
    BASE_URL = 'https://blockchain.info'
    
    def __init__(self):
        """Initialize Blockchain API client"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoPaymentSystem/1.0'
        })
    
    def validate_bitcoin_address(self, address: str) -> Dict:
        """Validate Bitcoin address and get address info
        
        Args:
            address: Bitcoin address to validate
            
        Returns:
            Dict: Address information
            
        Raises:
            CryptoAPIException: If validation fails
        """
        try:
            url = f"{self.BASE_URL}/q/addressbalance/{address}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # If we get here, address is valid
            balance_satoshis = int(response.text)
            balance_btc = Decimal(str(balance_satoshis)) / Decimal('100000000')
            
            logger.info(f"Bitcoin address {address} validated. Balance: {balance_btc} BTC")
            
            return {
                'address': address,
                'valid': True,
                'balance_btc': balance_btc,
                'balance_satoshis': balance_satoshis,
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # Address not found or invalid
                raise CryptoAPIException(f"Invalid Bitcoin address: {address}")
            raise CryptoAPIException(f"Blockchain API error: {str(e)}")
        except Exception as e:
            logger.error(f"Bitcoin address validation error: {str(e)}")
            raise CryptoAPIException(f"Failed to validate Bitcoin address: {str(e)}")
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        """Get Bitcoin transaction status
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dict: Transaction information
        """
        try:
            url = f"{self.BASE_URL}/rawtx/{tx_hash}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'hash': tx_hash,
                'confirmations': data.get('block_height', 0),
                'value_btc': Decimal(str(data.get('out', [{}])[0].get('value', 0))) / Decimal('100000000'),
                'status': 'confirmed' if data.get('block_height') else 'pending',
                'time': data.get('time'),
            }
            
        except Exception as e:
            logger.error(f"Failed to get transaction status: {str(e)}")
            raise CryptoAPIException(f"Failed to get transaction status: {str(e)}")


class EtherscanAPI:
    """Etherscan API client for Ethereum transactions and wallet validation"""
    
    BASE_URL = 'https://api.etherscan.io/api'
    
    def __init__(self, api_key: str = None):
        """Initialize Etherscan API client
        
        Args:
            api_key: Etherscan API key (get free key at etherscan.io)
        """
        self.api_key = api_key or 'YourEtherscanAPIKey'
        self.session = requests.Session()
    
    def validate_ethereum_address(self, address: str) -> Dict:
        """Validate Ethereum address and get balance
        
        Args:
            address: Ethereum address to validate
            
        Returns:
            Dict: Address information
            
        Raises:
            CryptoAPIException: If validation fails
        """
        try:
            # Validate format
            if not address.startswith('0x') or len(address) != 42:
                raise CryptoAPIException(f"Invalid Ethereum address format: {address}")
            
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest',
                'apikey': self.api_key,
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != '1':
                raise CryptoAPIException(f"Invalid Ethereum address: {address}")
            
            # Convert Wei to ETH (1 ETH = 10^18 Wei)
            balance_wei = int(data['result'])
            balance_eth = Decimal(str(balance_wei)) / Decimal('1000000000000000000')
            
            logger.info(f"Ethereum address {address} validated. Balance: {balance_eth} ETH")
            
            return {
                'address': address,
                'valid': True,
                'balance_eth': balance_eth,
                'balance_wei': balance_wei,
            }
            
        except Exception as e:
            logger.error(f"Ethereum address validation error: {str(e)}")
            raise CryptoAPIException(f"Failed to validate Ethereum address: {str(e)}")
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        """Get Ethereum transaction status
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dict: Transaction information
        """
        try:
            params = {
                'module': 'proxy',
                'action': 'eth_getTransactionByHash',
                'txhash': tx_hash,
                'apikey': self.api_key,
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'result' not in data or data['result'] is None:
                raise CryptoAPIException(f"Transaction not found: {tx_hash}")
            
            return {
                'hash': tx_hash,
                'status': 'pending' if data['result'].get('blockNumber') is None else 'confirmed',
                'from': data['result'].get('from'),
                'to': data['result'].get('to'),
                'value_eth': Decimal(int(data['result'].get('value', '0'), 16)) / Decimal('1000000000000000000'),
            }
            
        except Exception as e:
            logger.error(f"Failed to get Ethereum transaction status: {str(e)}")
            raise CryptoAPIException(f"Failed to get transaction status: {str(e)}")
