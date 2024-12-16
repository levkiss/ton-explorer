from abc import ABC, abstractmethod
from typing import Optional, Union, Set
from pathlib import Path
import pandas as pd
from pandas import DataFrame

class BaseDBManager(ABC):
    """Abstract base class for database managers."""
    
    @abstractmethod
    def _get_engine(self):
        """Get or create database engine."""
        pass
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def upload_dataframe(
        self,
        df: DataFrame,
        table_name: str,
        if_exists: str = 'append',
        chunk_size: int = 5000
    ) -> bool:
        """
        Upload pandas DataFrame to database table.

        Args:
            df: Pandas DataFrame to upload
            table_name: Target table name
            if_exists: How to behave if table exists
            chunk_size: Number of rows to insert at once

        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def upload_csv(
        self,
        file_path: Union[str, Path],
        table_name: str,
        if_exists: str = 'replace',
        chunk_size: int = 1000,
        **csv_kwargs
    ) -> bool:
        """
        Upload CSV file to database table.

        Args:
            file_path: Path to CSV file
            table_name: Target table name
            if_exists: How to behave if table exists
            chunk_size: Number of rows to insert at once
            csv_kwargs: Additional arguments for pd.read_csv()

        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def verify_upload(self, table_name: str, limit: int = 5) -> Optional[DataFrame]:
        """
        Verify data upload by retrieving sample rows.

        Args:
            table_name: Name of the table to verify
            limit: Number of rows to retrieve

        Returns:
            DataFrame with sample data if successful, None otherwise
        """
        pass
