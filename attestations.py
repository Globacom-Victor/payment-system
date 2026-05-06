import uuid
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, List
from enum import Enum
from crypto_api import EtherscanAPI, BlockchainAPI, CryptoAPIException

logger = logging.getLogger(__name__)


class AttestationStatus(Enum):
    """Attestation status enum"""
    PENDING = "pending"
    VERIFIED = "verified"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AttestationRecord:
    """Represents a blockchain attestation for a payment transaction"""
    
    def __init__(self, transaction_id: str, crypto_symbol: str, tx_hash: str, 
                 wallet_address: str, amount: Decimal, status: str = "pending"):
        self.attestation_id = str(uuid.uuid4())
        self.transaction_id = transaction_id
        self.crypto_symbol = crypto_symbol
        self.tx_hash = tx_hash
        self.wallet_address = wallet_address
        self.amount = amount
        self.status = status
        self.created_at = datetime.utcnow()
        self.verified_at = None
        self.confirmations = 0
        self.block_number = None
        self.gas_used = None
        self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert attestation to dictionary"""
        return {
            'attestation_id': self.attestation_id,
            'transaction_id': self.transaction_id,
            'crypto_symbol': self.crypto_symbol,
            'tx_hash': self.tx_hash,
            'wallet_address': self.wallet_address,
            'amount': str(self.amount),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'confirmations': self.confirmations,
            'block_number': self.block_number,
            'gas_used': self.gas_used,
            'metadata': self.metadata
        }


class AttestationService:
    """Service for managing blockchain attestations"""
    
    # Confirmation thresholds for different cryptocurrencies
    CONFIRMATION_THRESHOLDS = {
        'BTC': 6,      # Bitcoin - 6 confirmations ~1 hour
        'ETH': 12,     # Ethereum - 12 blocks ~3 minutes
        'LTC': 24,     # Litecoin - 24 confirmations ~1 hour
        'XRP': 1,      # Ripple - 1 confirmation (ledger-based)
    }
    
    def __init__(self, etherscan_api_key: str = None):
        """Initialize attestation service
        
        Args:
            etherscan_api_key: Etherscan API key for Ethereum attestations
        """
        self.etherscan = EtherscanAPI(api_key=etherscan_api_key)
        self.blockchain = BlockchainAPI()
        self.attestations = {}  # In-memory store (replace with DB in production)
    
    def create_attestation(self, transaction_id: str, crypto_symbol: str, 
                          tx_hash: str, wallet_address: str, amount: Decimal) -> AttestationRecord:
        """Create a new attestation record for a transaction
        
        Args:
            transaction_id: Transaction ID to attest
            crypto_symbol: Cryptocurrency symbol
            tx_hash: Blockchain transaction hash
            wallet_address: Destination wallet address
            amount: Transaction amount
            
        Returns:
            AttestationRecord: Created attestation
            
        Raises:
            ValueError: If invalid parameters
        """
        if not tx_hash or len(tx_hash) < 10:
            raise ValueError("Invalid transaction hash")
        
        if crypto_symbol not in self.CONFIRMATION_THRESHOLDS:
            raise ValueError(f"Unsupported cryptocurrency for attestation: {crypto_symbol}")
        
        attestation = AttestationRecord(
            transaction_id=transaction_id,
            crypto_symbol=crypto_symbol,
            tx_hash=tx_hash,
            wallet_address=wallet_address,
            amount=amount,
            status=AttestationStatus.PENDING.value
        )
        
        self.attestations[attestation.attestation_id] = attestation
        logger.info(f"Attestation created: {attestation.attestation_id} for transaction {transaction_id}")
        
        return attestation
    
    def verify_ethereum_attestation(self, attestation_id: str) -> Dict:
        """Verify an Ethereum transaction attestation
        
        Args:
            attestation_id: Attestation ID to verify
            
        Returns:
            Dict: Verification result
            
        Raises:
            ValueError: If attestation not found
        """
        attestation = self._get_attestation(attestation_id)
        
        if attestation.crypto_symbol != 'ETH':
            raise ValueError("This method is for Ethereum attestations only")
        
        try:
            logger.info(f"Verifying Ethereum attestation: {attestation_id}")
            tx_status = self.etherscan.get_transaction_status(attestation.tx_hash)
            
            # Update attestation with verified data
            attestation.status = AttestationStatus.VERIFIED.value
            attestation.verified_at = datetime.utcnow()
            attestation.metadata['from'] = tx_status.get('from')
            attestation.metadata['to'] = tx_status.get('to')
            attestation.metadata['value_eth'] = str(tx_status.get('value_eth'))
            
            # Check if confirmed
            if tx_status['status'] == 'confirmed':
                attestation.status = AttestationStatus.CONFIRMED.value
                attestation.confirmations = self.CONFIRMATION_THRESHOLDS['ETH']
                logger.info(f"Ethereum attestation confirmed: {attestation_id}")
            
            return attestation.to_dict()
            
        except CryptoAPIException as e:
            logger.error(f"Failed to verify Ethereum attestation: {str(e)}")
            attestation.status = AttestationStatus.FAILED.value
            return attestation.to_dict()
    
    def verify_bitcoin_attestation(self, attestation_id: str) -> Dict:
        """Verify a Bitcoin transaction attestation
        
        Args:
            attestation_id: Attestation ID to verify
            
        Returns:
            Dict: Verification result
            
        Raises:
            ValueError: If attestation not found
        """
        attestation = self._get_attestation(attestation_id)
        
        if attestation.crypto_symbol != 'BTC':
            raise ValueError("This method is for Bitcoin attestations only")
        
        try:
            logger.info(f"Verifying Bitcoin attestation: {attestation_id}")
            tx_status = self.blockchain.get_transaction_status(attestation.tx_hash)
            
            # Update attestation with verified data
            attestation.status = AttestationStatus.VERIFIED.value
            attestation.verified_at = datetime.utcnow()
            attestation.confirmations = tx_status.get('confirmations', 0)
            attestation.metadata['value_btc'] = str(tx_status.get('value_btc'))
            attestation.metadata['confirmations'] = attestation.confirmations
            
            # Check if enough confirmations
            if attestation.confirmations >= self.CONFIRMATION_THRESHOLDS['BTC']:
                attestation.status = AttestationStatus.CONFIRMED.value
                logger.info(f"Bitcoin attestation confirmed: {attestation_id}")
            
            return attestation.to_dict()
            
        except CryptoAPIException as e:
            logger.error(f"Failed to verify Bitcoin attestation: {str(e)}")
            attestation.status = AttestationStatus.FAILED.value
            return attestation.to_dict()
    
    def verify_attestation(self, attestation_id: str) -> Dict:
        """Verify attestation based on cryptocurrency type
        
        Args:
            attestation_id: Attestation ID to verify
            
        Returns:
            Dict: Verification result
        """
        attestation = self._get_attestation(attestation_id)
        
        if attestation.crypto_symbol == 'ETH':
            return self.verify_ethereum_attestation(attestation_id)
        elif attestation.crypto_symbol == 'BTC':
            return self.verify_bitcoin_attestation(attestation_id)
        else:
            logger.warning(f"Attestation verification not implemented for {attestation.crypto_symbol}")
            return attestation.to_dict()
    
    def get_attestation(self, attestation_id: str) -> Dict:
        """Get attestation record
        
        Args:
            attestation_id: Attestation ID
            
        Returns:
            Dict: Attestation data
            
        Raises:
            ValueError: If attestation not found
        """
        attestation = self._get_attestation(attestation_id)
        return attestation.to_dict()
    
    def get_attestations_by_transaction(self, transaction_id: str) -> List[Dict]:
        """Get all attestations for a transaction
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            List[Dict]: List of attestations
        """
        attestations = [
            att.to_dict() for att in self.attestations.values()
            if att.transaction_id == transaction_id
        ]
        logger.info(f"Found {len(attestations)} attestations for transaction {transaction_id}")
        return attestations
    
    def cancel_attestation(self, attestation_id: str) -> Dict:
        """Cancel an attestation
        
        Args:
            attestation_id: Attestation ID to cancel
            
        Returns:
            Dict: Cancelled attestation
        """
        attestation = self._get_attestation(attestation_id)
        attestation.status = AttestationStatus.CANCELLED.value
        logger.info(f"Attestation cancelled: {attestation_id}")
        return attestation.to_dict()
    
    def get_attestation_status(self, attestation_id: str) -> str:
        """Get current status of an attestation
        
        Args:
            attestation_id: Attestation ID
            
        Returns:
            str: Current status
        """
        attestation = self._get_attestation(attestation_id)
        return attestation.status
    
    def is_attestation_confirmed(self, attestation_id: str) -> bool:
        """Check if attestation is confirmed
        
        Args:
            attestation_id: Attestation ID
            
        Returns:
            bool: True if confirmed
        """
        attestation = self._get_attestation(attestation_id)
        return attestation.status == AttestationStatus.CONFIRMED.value
    
    def get_all_attestations(self) -> List[Dict]:
        """Get all attestations
        
        Returns:
            List[Dict]: All attestations
        """
        return [att.to_dict() for att in self.attestations.values()]
    
    def get_confirmed_attestations(self) -> List[Dict]:
        """Get all confirmed attestations
        
        Returns:
            List[Dict]: Confirmed attestations
        """
        return [
            att.to_dict() for att in self.attestations.values()
            if att.status == AttestationStatus.CONFIRMED.value
        ]
    
    def _get_attestation(self, attestation_id: str) -> AttestationRecord:
        """Get attestation by ID (internal)
        
        Args:
            attestation_id: Attestation ID
            
        Returns:
            AttestationRecord: Attestation object
            
        Raises:
            ValueError: If attestation not found
        """
        attestation = self.attestations.get(attestation_id)
        if not attestation:
            raise ValueError(f"Attestation not found: {attestation_id}")
        return attestation
