import asyncio
from src.ton import run_loader

HOST_ADDRESS = "some_address"

async def main():
    await run_loader(HOST_ADDRESS)

if __name__ == "__main__":
    asyncio.run(main())