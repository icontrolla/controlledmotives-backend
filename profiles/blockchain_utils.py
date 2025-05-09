from web3 import Web3
from django.conf import settings
import logging

# Set up logging for better debugging
logger = logging.getLogger(__name__)


class BlockchainService:
    def __init__(self):
        try:
            # Use settings.WEB3_PROVIDER_URI for the provider URL
            provider_uri = getattr(settings, 'https://mainnet.infura.io/v3/8ef5e4fb0439434689a82173b044b334', 'http://127.0.0.1:8545')  # Fallback to local node
            logger.info(f"Attempting to connect to Web3 provider at {provider_uri}")
            self.w3 = Web3(Web3.HTTPProvider(provider_uri))

            if not self.w3.is_connected():
                logger.error(f"Failed to connect to Web3 provider at {provider_uri}")
                raise ConnectionError(f"Failed to connect to Web3 provider at {provider_uri}")

            # Load contract address and ABI from settings
            contract_address = getattr(settings, 'CONTRACT_ADDRESS', None)
            contract_abi = getattr(settings, 'CONTRACT_ABI', None)
            if not contract_address or not contract_abi:
                raise ValueError("CONTRACT_ADDRESS or CONTRACT_ABI not set in settings")

            self.contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
            logger.info(f"Successfully connected to Web3 provider and loaded contract at {contract_address}")
        except Exception as e:
            logger.error(f"BlockchainService initialization failed: {str(e)}")
            raise

    def get_artwork_price(self):
        try:
            price_wei = self.contract.functions.price().call()
            return price_wei
        except Exception as e:
            logger.error(f"Error getting artwork price: {str(e)}")
            raise Exception(f"Error getting price: {e}")

    def buy_artwork(self, from_address, value_wei):
        try:
            tx = {
                'from': from_address,
                'value': value_wei,
                'gas': 200000,  # Add a reasonable gas limit
                'gasPrice': self.w3.eth.gas_price,  # Use current gas price
                'nonce': self.w3.eth.get_transaction_count(from_address),
            }
            tx_hash = self.contract.functions.buyArtwork().transact(tx)
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            return tx_hash
        except Exception as e:
            logger.error(f"Error buying artwork: {str(e)}")
            raise Exception(f"Error buying artwork: {e}")


# Lazy initialization
blockchain_service = None


def get_blockchain_service():
    global blockchain_service
    if blockchain_service is None:
        try:
            blockchain_service = BlockchainService()
        except Exception as e:
            logger.error(f"Failed to initialize BlockchainService: {str(e)}")
            raise
    return blockchain_service