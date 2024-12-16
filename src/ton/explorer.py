from datetime import datetime
import aiohttp
import pandas as pd
import asyncio
import random
from pytoniq_core import Address
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Dict, Any, List, Optional

from .base import BlockchainExplorer
from .exceptions import TonAPIError
from ..utils.logging import logger

class TonExplorer(BlockchainExplorer):
    """TON blockchain explorer implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://tonapi.io/v2"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @retry(
            retry=retry_if_exception_type(TonAPIError),
            stop=stop_after_attempt(5), 
            wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request with error handling."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                url = f"{self.base_url}/{endpoint}"
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise TonAPIError(f"API request failed: {response.status}")
                    return await response.json()
            except Exception as e:
                logger.error(f"API request failed: {str(e)}")
                raise TonAPIError(str(e))
            
    @staticmethod
    def format_address(raw_address: str) -> str:
        """Converts a raw TON address to a human-readable address."""
        return Address(raw_address).to_str(is_user_friendly=True, is_bounceable=False, is_url_safe=True)

    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information."""
        endpoint = f"blockchain/accounts/{address}"
        return await self._make_request(endpoint)

    async def get_account_transactions(
        self, 
        address: str, 
        limit: int = 1000
    ) -> pd.DataFrame:
        """Get account transactions."""
        all_transactions = []
        after_lt = 0
        logger.info(f"Fetching transactions for {address}")

        while True:
            params = {
                "limit": limit,
                "after_lt": after_lt,
                "sort_order": "asc"
            }
            
            endpoint = f"blockchain/accounts/{address}/transactions"
            response = await self._make_request(endpoint, params)

            transactions = response.get('transactions', [])
            if not transactions:
                break

            all_transactions.extend(transactions)
            after_lt = transactions[-1].get('lt')
            
            if len(transactions) < limit:
                break
                
            await asyncio.sleep(random.uniform(0.05, 0.4))  # Rate limiting
            
        return pd.json_normalize(all_transactions, sep='_') if all_transactions else pd.DataFrame()

    async def get_transaction_info(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction details."""
        endpoint = f"blockchain/transactions/{tx_hash}"
        return await self._make_request(endpoint)

    def extract_transfers(self, transactions: List[Dict]) -> pd.DataFrame:
        """Extract transfers from transactions."""
        transfers = []
        
        for tx in transactions:
            base_info = {
                'tx_hash': tx.get('hash'),
                'timestamp': datetime.fromtimestamp(tx.get('utime', 0)),
                'lt': tx.get('lt'),
                'tx_type': tx.get('transaction_type'),
                'success': tx.get('success', False),
                'fees': float(tx.get('total_fees', 0)) / 1e9,
                'balance_change': float(tx.get('balance_change', {}).get('old_balance', 0)) / 1e9
            }
            
            # Process incoming message
            if in_msg := tx.get('in_msg'):
                transfer = {**base_info}
                transfer.update(self._process_message(in_msg, is_incoming=True))
                transfers.append(transfer)
            
            # Process outgoing messages
            for out_msg in tx.get('out_msgs', []):
                transfer = {**base_info}
                transfer.update(self._process_message(out_msg, is_incoming=False))
                transfers.append(transfer)
                
        return pd.DataFrame(transfers)

    def _process_message(self, msg: Dict, is_incoming: bool) -> Dict[str, Any]:
        """Helper method to process transaction messages."""
        return {
            'from_address': msg.get('source'),
            'to_address': msg.get('destination'),
            'amount': float(msg.get('value', 0)) / 1e9,
            'direction': 'incoming' if is_incoming else 'outgoing',
            'op_code': msg.get('op_code'),
            'op_name': msg.get('decoded_op_name'),
            'comment': msg.get('decoded_body', {}).get('text', ''),
            'is_internal': msg.get('msg_type') == 'internal'
        }