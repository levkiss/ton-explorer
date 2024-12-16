# TON Analytics Tool

A Python-based tool for analyzing TON blockchain transactions. It fetches transaction data from the TON blockchain and stores it in a PostgreSQL database for further analysis.

## Features

- Asynchronous TON blockchain data fetching
- Automatic transaction processing for specified addresses
- Recipient transaction tracking
- PostgreSQL storage with automatic schema updates
- Built-in analytics queries
- Database optimization tools

## Installation

1. Clone the repository     
```bash
git clone https://github.com/ton-analytics/ton-analytics.git
cd ton-analytics
```

2. Install dependencies
```bash
poetry install
```

3. Set up environment variables
```bash
cp .env.example .env
```

4. Start PostgreSQL server
```bash
docker compose up -d
```

5. Run the tool
```bash
poetry run python src/main.py
```


## Usage
### Fetching transactions

```python
import asyncio
from src.ton.loader import TransactionLoader

async def main():
    loader = TransactionLoader()
    await loader.fetch_transactions()

asyncio.run(main())
```