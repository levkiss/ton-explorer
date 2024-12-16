from typing import List
import asyncio
import pandas as pd
import ast

from .explorer import TonExplorer
from .exceptions import TonDataError
from .mapping import DEFAULT_TRANSACTION_COLUMNS, DEFAULT_OUT_MSG_COLUMNS
from ..db import get_postgres_manager
from ..utils import logger

class TransactionLoader:
    """Class for loading and storing TON transactions."""
    
    def __init__(
        self,
        explorer: TonExplorer,
        batch_size: int = 10,
        batch_delay: float = 0.1
    ):
        self.explorer = explorer
        self.db = get_postgres_manager()
        self.batch_size = batch_size
        self.batch_delay = batch_delay

    def _prepare_transaction_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare transaction dataframe with selected columns."""
        available_cols = [col for col in DEFAULT_TRANSACTION_COLUMNS if col in df.columns]
        return df[available_cols]

    def _prepare_out_msg_df(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Extract and prepare out_messages dataframe from transactions."""
        try:
            # Convert string representation of lists to actual lists
            transactions_df['out_msgs'] = transactions_df['out_msgs'].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            
            # Explode the out_msgs column to create separate rows for each message
            exploded_df = transactions_df[['hash', 'out_msgs']].explode('out_msgs')
            
            # Normalize the JSON-like dictionary structure
            out_msgs_df = pd.json_normalize(
                exploded_df['out_msgs'].dropna(),
                sep='_'
            )
            
            # Filter and rename columns based on DEFAULT_OUT_MSG_COLUMNS
            available_cols = [col for col in DEFAULT_OUT_MSG_COLUMNS if col in out_msgs_df.columns]
            
            res_df = out_msgs_df[available_cols]

            return res_df

        except Exception as e:
            print(f"Error preparing out messages dataframe: {e}")
            return pd.DataFrame(columns=DEFAULT_OUT_MSG_COLUMNS)

    async def process_address(self, address: str) -> None:
        """Process transactions for a single address."""
        try:
            # Get transactions
            transactions_df = await self.explorer.get_account_transactions(address)
            if transactions_df.empty:
                logger.info(f"No transactions found for address: {address}")
                return
            
            tx_df = self._prepare_transaction_df(transactions_df)
            out_msgs_df = self._prepare_out_msg_df(transactions_df)

            # Store in database only if dataframes have data
            if not tx_df.empty: 
                self.db.upload_dataframe(
                    df = tx_df,
                    table_name = 'transactions',
                    if_exists='append'
                )
                
            if not out_msgs_df.empty:  
                self.db.upload_dataframe(
                    df = out_msgs_df,
                    table_name = 'out_msgs',
                    if_exists='append'
                )
            
            logger.info(f"Processed {len(transactions_df)} transactions for {address}")
            
        except Exception as e:
            logger.error(f"Error processing address {address}: {str(e)}")
            raise TonDataError(f"Failed to process address {address}: {str(e)}")

    async def process_addresses(self, addresses: List[str]) -> None:
        """Process multiple addresses in batches."""
        # Filter out already processed addresses
        processed = self.db.get_processed_addresses()
        addresses = [addr for addr in addresses if addr not in processed]
        
        if not addresses:
            logger.info("No new addresses to process")
            return

        # Process in batches
        batches = [
            addresses[i:i + self.batch_size] 
            for i in range(0, len(addresses), self.batch_size)
        ]
        
        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)}")
            
            tasks = [self.process_address(addr) for addr in batch]
            await asyncio.gather(*tasks)
            
            if batch_num < len(batches):
                await asyncio.sleep(self.batch_delay)

    async def process_recipient_transactions(self, host_address: str) -> None:
        """Process transactions for all recipients of a host address."""
        try:
            # Get host transactions
            host_df = await self.explorer.get_account_transactions(host_address)
            if host_df.empty:
                logger.info(f"No transactions found for host address: {host_address}")
                return
            
            logger.info(f"Fetched {len(host_df)} transactions for {host_address}")
            
            # Collect unique recipient addresses
            recipient_addresses = []

            # Extract recipient addresses
            for row in host_df["out_msgs"].to_list():
                if isinstance(row, str):
                    row_dict = ast.literal_eval(row)
                else:
                    row_dict = row
                for msg in row_dict:
                    if isinstance(msg, dict) and 'destination' in msg:
                        dest_addr = msg['destination'].get('address')
                        if dest_addr:
                            recipient_addresses.append(dest_addr)

            logger.info(f"Found {len(recipient_addresses)} unique recipient addresses for {host_address}")

            # Process recipient addresses
            await self.process_addresses(list(recipient_addresses))
            
        except Exception as e:
            logger.error(f"Error processing recipients for {host_address}: {str(e)}")
            raise TonDataError(f"Failed to process recipients: {str(e)}")

    @classmethod
    async def main(cls, api_key: str, host_address: str) -> None:
        """Main entry point for processing transactions."""
        explorer = TonExplorer(api_key)
        loader = cls(explorer)
        
        try:
            await loader.process_recipient_transactions(host_address)
            logger.info("Transaction processing completed successfully")
        except Exception as e:
            logger.error(f"Transaction processing failed: {str(e)}")
        finally:
            loader.db.close()