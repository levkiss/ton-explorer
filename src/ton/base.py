from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd

class BlockchainExplorer(ABC):
    """Base class for blockchain explorers."""
    
    @abstractmethod
    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information."""
        pass
    
    @abstractmethod
    async def get_account_transactions(
        self, 
        address: str, 
        limit: int = 100
    ) -> pd.DataFrame:
        """Get account transactions."""
        pass
    
    @abstractmethod
    async def get_transaction_info(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction details."""
        pass
    
    @abstractmethod
    def extract_transfers(self, transactions: List[Dict]) -> pd.DataFrame:
        """Extract transfers from transactions."""
        pass