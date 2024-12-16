import asyncio
import sys
from typing import Optional
from argparse import ArgumentParser

from src.ton import TransactionLoader
from src.utils import settings, logger

async def run_loader(host_address: Optional[str] = None) -> None:
    """
    Run transaction loader for a given host address.
    
    Args:
        host_address: TON wallet address to process. If None, uses command line argument.
    """
    parser = ArgumentParser(description="Run transaction loader for a given host address.")
    parser.add_argument("host_address", type=str, nargs="?", help="TON wallet address to process")
    args = parser.parse_args()

    if not host_address:
        if not args.host_address:
            logger.error("Please provide a host address as argument")
            sys.exit(1)
        host_address = args.host_address

    try:
        logger.info(f"Starting transaction processing for host: {host_address}")
        logger.info(f"Using API key: {settings.TON_API_KEY}")
        await TransactionLoader.main(
            api_key=settings.TON_API_KEY,
            host_address=host_address
        )
    except Exception as e:
        logger.error(f"Failed to process transactions: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_loader())