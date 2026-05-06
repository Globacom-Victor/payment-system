"""
Attestation Usage Examples
Demonstrates how to use the attestation system in your payment flow
"""

# Example 1: Create a payment transaction
from payment_service_v2 import PaymentServiceV2
from sqlalchemy.orm import Session

def example_create_payment(db_session: Session):
    """Example: Create a payment and attestation"""
    payment_service = PaymentServiceV2(session=db_session)
    
    # Create a cryptocurrency purchase
    transaction = payment_service.create_purchase(
        crypto_symbol='ETH',
        fiat_symbol='USD',
        fiat_amount=1000.00,
        wallet_address='0x742d35Cc6634C0532925a3b844Bc9e7595f42e24',
        customer_email='customer@example.com'
    )
    
    print(f"Transaction created: {transaction.id}")
    print(f"Amount: {transaction.crypto_amount} {transaction.crypto_symbol}")
    
    return transaction


# Example 2: Create an attestation for a transaction
def example_create_attestation(db_session: Session, transaction_id: str):
    """Example: Create blockchain attestation for a transaction"""
    payment_service = PaymentServiceV2(session=db_session)
    
    # After transaction is processed and has a blockchain hash
    attestation = payment_service.attest_transaction(
        transaction_id=transaction_id,
        tx_hash='0xabc123def456abc123def456abc123def456abc123def456abc123def456abc1'
    )
    
    print(f"Attestation created: {attestation['attestation_id']}")
    print(f"Status: {attestation['status']}")
    
    return attestation['attestation_id']


# Example 3: Verify an attestation
def example_verify_attestation(db_session: Session, attestation_id: str):
    """Example: Verify blockchain attestation"""
    payment_service = PaymentServiceV2(session=db_session)
    
    # Verify the attestation on the blockchain
    result = payment_service.verify_attestation(attestation_id)
    
    print(f"Attestation verification result:")
    print(f"  Status: {result['status']}")
    print(f"  Confirmations: {result['confirmations']}")
    print(f"  Verified at: {result['verified_at']}")
    
    return result


# Example 4: Get attestations for a transaction
def example_get_attestations(db_session: Session, transaction_id: str):
    """Example: Retrieve all attestations for a transaction"""
    payment_service = PaymentServiceV2(session=db_session)
    
    attestations = payment_service.get_attestations(transaction_id)
    
    print(f"Found {len(attestations)} attestation(s) for transaction {transaction_id}:")
    for attestation in attestations:
        print(f"  - {attestation['attestation_id']}: {attestation['status']}")
    
    return attestations


# Example 5: Complete payment flow with attestation
def example_complete_payment_flow(db_session: Session):
    """Example: Complete flow from payment creation to attestation confirmation"""
    payment_service = PaymentServiceV2(session=db_session)
    
    print("=== Payment Flow with Attestation ===\n")
    
    # Step 1: Create transaction
    print("Step 1: Creating payment transaction...")
    transaction = payment_service.create_purchase(
        crypto_symbol='BTC',
        fiat_symbol='USD',
        fiat_amount=50000.00,
        wallet_address='bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',
        customer_email='customer@example.com'
    )
    print(f"✓ Transaction created: {transaction.id}")
    print(f"  Amount: {transaction.crypto_amount} BTC = ${transaction.fiat_amount}\n")
    
    # Step 2: Simulate payment processing
    print("Step 2: Processing payment on blockchain...")
    tx_hash = '000000000000000000abc123def456abc123def456abc123def456abc123def456'
    
    # Step 3: Create attestation
    print(f"Step 3: Creating attestation...")
    attestation = payment_service.attest_transaction(
        transaction_id=transaction.id,
        tx_hash=tx_hash
    )
    attestation_id = attestation['attestation_id']
    print(f"✓ Attestation created: {attestation_id}")
    print(f"  Status: {attestation['status']}\n")
    
    # Step 4: Verify attestation (would check blockchain)
    print("Step 4: Verifying attestation on blockchain...")
    verification = payment_service.verify_attestation(attestation_id)
    print(f"✓ Attestation verified")
    print(f"  Status: {verification['status']}")
    print(f"  Confirmations: {verification['confirmations']}")
    print(f"  Verified at: {verification['verified_at']}\n")
    
    # Step 5: Check final transaction status
    print("Step 5: Checking final transaction status...")
    updated_transaction = payment_service.get_transaction_status(transaction.id)
    print(f"✓ Transaction status: {updated_transaction.status}")
    print(f"  Last updated: {updated_transaction.updated_at}\n")
    
    print("=== Payment Flow Complete ===")
    
    return {
        'transaction': transaction,
        'attestation': attestation,
        'verification': verification
    }


# Example 6: Handle multiple attestations
def example_multiple_attestations(db_session: Session, transaction_id: str):
    """Example: Re-attest or manage multiple attestations for a transaction"""
    payment_service = PaymentServiceV2(session=db_session)
    
    # Get existing attestations
    existing_attestations = payment_service.get_attestations(transaction_id)
    print(f"Existing attestations: {len(existing_attestations)}")
    
    for att in existing_attestations:
        print(f"  - {att['attestation_id']}: {att['status']}")
    
    # Cancel an old attestation if needed
    if existing_attestations:
        old_att_id = existing_attestations[0]['attestation_id']
        cancelled = payment_service.cancel_attestation(old_att_id)
        print(f"\nCancelled attestation: {cancelled['attestation_id']}")
    
    return existing_attestations


# Configuration for different cryptos
ATTESTATION_CONFIG = {
    'BTC': {
        'description': 'Bitcoin',
        'min_confirmations': 6,
        'confirmation_time': '~1 hour',
        'api': 'blockchain.info'
    },
    'ETH': {
        'description': 'Ethereum',
        'min_confirmations': 12,
        'confirmation_time': '~3 minutes',
        'api': 'etherscan.io'
    },
    'LTC': {
        'description': 'Litecoin',
        'min_confirmations': 24,
        'confirmation_time': '~1 hour',
        'api': 'blockchain.info'
    },
    'XRP': {
        'description': 'Ripple',
        'min_confirmations': 1,
        'confirmation_time': '~5 seconds',
        'api': 'xrpl.org'
    },
}


if __name__ == '__main__':
    print("""
    Attestation System Usage Guide
    ==============================
    
    This module provides examples for using blockchain attestations in payment processing.
    
    Key Functions:
    1. attest_transaction() - Create attestation for a payment
    2. verify_attestation() - Verify attestation on blockchain
    3. get_attestations() - Retrieve attestations for a transaction
    4. cancel_attestation() - Cancel an attestation
    
    Supported Cryptocurrencies:
    """)
    
    for crypto, config in ATTESTATION_CONFIG.items():
        print(f"\n  {crypto} ({config['description']})")
        print(f"    - Min Confirmations: {config['min_confirmations']}")
        print(f"    - Avg Time: {config['confirmation_time']}")
        print(f"    - Verified via: {config['api']}")
