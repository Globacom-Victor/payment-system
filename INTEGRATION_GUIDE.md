# Real Cryptocurrency API Integration Guide

## 🔌 Integrated APIs

This system integrates with three major cryptocurrency APIs:

### 1. **CoinGecko API** 📊
- **Purpose**: Real-time exchange rates and market data
- **Features**:
  - Live price data for 1000+ cryptocurrencies
  - Market cap, 24h volume, price changes
  - No authentication required (free tier)
  - Rate limiting: ~10-50 calls/minute

**CoinGecko Supported Cryptos**:
- BTC (Bitcoin)
- ETH (Ethereum)
- LTC (Litecoin)
- XRP (Ripple)
- USDC (USD Coin)
- USDT (Tether)

**CoinGecko Supported Fiats**:
- USD, EUR, GBP, JPY, CAD, AUD, and 150+ more

### 2. **Blockchain.com API** ⛓️
- **Purpose**: Bitcoin transaction validation and monitoring
- **Features**:
  - Wallet address validation
  - Balance checking
  - Transaction status tracking
  - No authentication required (free tier)

**Supported Cryptocurrencies**:
- BTC (Bitcoin)
- LTC (Litecoin) - via partners

### 3. **Etherscan API** 🔗
- **Purpose**: Ethereum blockchain interaction
- **Features**:
  - Wallet address validation
  - Balance checking
  - Transaction status
  - Smart contract interaction
  - Requires free API key

**Getting Etherscan API Key**:
1. Visit https://etherscan.io/apis
2. Sign up for a free account
3. Create API key
4. Add to `.env`: `ETHERSCAN_API_KEY=your_key_here`

## 🚀 Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Required: PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_payment

# Optional: Etherscan API Key (for Ethereum validation)
ETHERSCAN_API_KEY=your_key_from_etherscan

# Optional: CoinGecko Cache TTL (seconds)
COINGECKO_CACHE_TTL=60
```

### Step 3: Initialize Database
```bash
python setup_db.py
```

## 📊 Usage Examples

### Create a Purchase with Real Exchange Rates
```bash
# Bitcoin purchase
python cli_v2.py purchase --crypto BTC --fiat USD --amount 100 --wallet bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v

# Ethereum purchase
python cli_v2.py purchase --crypto ETH --fiat EUR --amount 500 --wallet 0x742d35Cc6634C0532925a3b844Bc029e4f27d9B4

# Litecoin purchase
python cli_v2.py purchase --crypto LTC --fiat USD --amount 50 --wallet LLvgzwwcjRB8MUHvBXEMQB5hW4hZPnJr3s
```

### Get Real-Time Market Data
```bash
python cli_v2.py market --crypto BTC --fiat USD
python cli_v2.py market --crypto ETH --fiat EUR
python cli_v2.py market --crypto LTC --fiat GBP
```

### Check Transaction Status
```bash
python cli_v2.py status --transaction-id a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6
```

### List All Transactions
```bash
python cli_v2.py list
```

## 🔐 API Integration Architecture

### crypto_api.py
Contains three API client classes:

#### CoinGeckoAPI
```python
from crypto_api import CoinGeckoAPI

api = CoinGeckoAPI(cache_ttl=60)

# Get exchange rate
rate = api.get_exchange_rate('BTC', 'USD')
print(f"1 BTC = ${rate} USD")

# Get market data
data = api.get_market_data('ETH', 'EUR')
print(data['price'])  # Current price
print(data['market_cap'])  # Market cap
print(data['volume_24h'])  # 24h volume
```

#### BlockchainAPI
```python
from crypto_api import BlockchainAPI

api = BlockchainAPI()

# Validate Bitcoin address
info = api.validate_bitcoin_address('bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v')
print(info['balance_btc'])  # Current balance

# Get transaction status
status = api.get_transaction_status('tx_hash_here')
print(status['confirmations'])
```

#### EtherscanAPI
```python
from crypto_api import EtherscanAPI

api = EtherscanAPI(api_key='your_etherscan_key')

# Validate Ethereum address
info = api.validate_ethereum_address('0x742d35Cc6634C0532925a3b844Bc029e4f27d9B4')
print(info['balance_eth'])  # Current balance in ETH

# Get transaction status
status = api.get_transaction_status('tx_hash_here')
print(status['status'])  # 'pending' or 'confirmed'
```

### payment_service_v2.py
Enhanced payment service with API integration:

```python
from payment_service_v2 import PaymentServiceV2
from database import get_session

session = get_session()
service = PaymentServiceV2(session)

# Creates purchase with:
# 1. Real-time exchange rates from CoinGecko
# 2. Wallet validation from blockchain APIs
# 3. Automatic database persistence
transaction = service.create_purchase(
    crypto_symbol='BTC',
    fiat_symbol='USD',
    fiat_amount=100,
    wallet_address='bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v'
)

# Get market data
market = service.get_market_data('BTC', 'USD')
```

## 🔄 API Response Caching

CoinGecko responses are cached to:
- Improve performance
- Reduce API calls
- Stay within rate limits

**Cache Configuration**:
```python
# Default: 60 seconds
api = CoinGeckoAPI(cache_ttl=60)

# Custom: 5 minutes
api = CoinGeckoAPI(cache_ttl=300)
```

## ⚠️ Error Handling

The system handles API errors gracefully:

```python
from crypto_api import CryptoAPIException

try:
    rate = api.get_exchange_rate('BTC', 'USD')
except CryptoAPIException as e:
    print(f"API Error: {e}")
    # Fallback logic here
```

## 📝 Logging

All API calls are logged for debugging:

```bash
# View logs
tail -f crypto_payment.log

# Enable debug logging
LOG_LEVEL=DEBUG python cli_v2.py purchase ...
```

## 🚨 Rate Limiting

**CoinGecko**:
- Free tier: ~10-50 calls/minute
- Caching helps reduce calls

**Etherscan**:
- Free tier: 5 calls/second
- Premium tiers available

**Blockchain.com**:
- Free tier: No strict limits
- Recommended: < 1000 calls/day

## 🔗 API Documentation

- **CoinGecko**: https://www.coingecko.com/en/api
- **Blockchain.com**: https://www.blockchain.com/en/api
- **Etherscan**: https://docs.etherscan.io/

## 💡 Future Enhancements

1. **Webhook Support**: Real-time transaction confirmations
2. **More Blockchains**: Litecoin, Ripple, Polkadot APIs
3. **Price Alerts**: Notify when price reaches targets
4. **Historical Data**: Store price history
5. **Fee Estimation**: Real-time network fees
6. **Multi-signature**: Enhanced security
7. **Mobile App**: React Native client
8. **WebSocket Support**: Live price streams

## ✅ Testing

Test the integration:

```bash
# Test with small amounts first
python cli_v2.py purchase --crypto BTC --fiat USD --amount 1 --wallet bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v

# Check market data
python cli_v2.py market --crypto BTC --fiat USD

# View transaction
python cli_v2.py list
```
