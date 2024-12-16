from typing import Optional, Union, Set
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import SQLAlchemyError
from pandas import DataFrame

from .base import BaseDBManager
from ..utils import logger

class PostgresManager(BaseDBManager):
    """PostgreSQL database manager implementation."""

    def __init__(
        self,
        db_user: str,
        db_password: str,
        db_host: str,
        db_port: str,
        db_name: str
    ) -> None:
        """
        Initialize PostgreSQL connection manager.

        Args:
            db_user: Database username
            db_password: Database password
            db_host: Database host address
            db_port: Database port
            db_name: Database name
        """
        self.connection_string = (
            f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        )
        self.engine: Optional[Engine] = None

    def connect(self) -> None:
        """Establish database connection."""
        try:
            self._get_engine()
            logger.info("Database connection established")
        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def _get_engine(self) -> Engine:
        """
        Get or create SQLAlchemy engine.

        Returns:
            SQLAlchemy engine instance
        """
        if not self.engine:
            self.engine = create_engine(self.connection_string)
        return self.engine

    def _add_missing_columns(self, df: DataFrame, table_name: str) -> None:
        """
        Add missing columns to the table if they don't exist.
        
        Args:
            df: DataFrame containing new data
            table_name: Name of the target table
        """
        engine = self._get_engine()
        
        with engine.connect() as connection:
            existing_columns = connection.execute(text(
                f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                """
            )).fetchall()
            existing_columns = {col[0] for col in existing_columns}

            df_columns = set(df.columns)
            missing_columns = df_columns - existing_columns

            if missing_columns:
                for col in missing_columns:
                    connection.execute(text(
                        f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN IF NOT EXISTS "{col}" TEXT
                        """
                    ))
                connection.commit()
                logger.info(f"Added missing columns: {missing_columns}")

    def upload_dataframe(
        self,
        df: DataFrame,
        table_name: str,
        if_exists: str = 'append',
        chunk_size: int = 5000
    ) -> bool:
        try:
            engine = self._get_engine()

            if if_exists == 'append':
                with engine.connect() as connection:
                    exists = connection.execute(text(
                        f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table_name}'
                        )
                        """
                    )).scalar()
                    
                    if exists:
                        self._add_missing_columns(df, table_name)

            df.to_sql(
                name=table_name,
                con=engine,
                if_exists=if_exists,
                index=False,
                chunksize=chunk_size,
                method='multi'
            )
            
            logger.info(f"Successfully uploaded data to table: {table_name}")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error uploading data to table {table_name}: {str(e)}")
            return False

    def upload_csv(
        self,
        file_path: Union[str, Path],
        table_name: str,
        if_exists: str = 'replace',
        chunk_size: int = 1000,
        **csv_kwargs
    ) -> bool:
        try:
            df = pd.read_csv(file_path, **csv_kwargs)
            return self.upload_dataframe(
                df=df,
                table_name=table_name,
                if_exists=if_exists,
                chunk_size=chunk_size
            )

        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            return False

    def verify_upload(self, table_name: str, limit: int = 5) -> Optional[DataFrame]:
        try:
            engine = self._get_engine()
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return pd.read_sql(query, engine)

        except SQLAlchemyError as e:
            logger.error(f"Error verifying upload for table {table_name}: {str(e)}")
            return None

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            logger.info("Database connection closed")

    def get_processed_addresses(self, table_name: str = 'transactions') -> Set[str]:
        try:
            engine = self._get_engine()
            query = f"""
            SELECT DISTINCT account_address 
            FROM {table_name} 
            WHERE account_address IS NOT NULL
            """
            
            with engine.connect() as connection:
                result = connection.execute(text(query))
                addresses = {row[0] for row in result}
                return addresses
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting processed addresses: {str(e)}")
            return set()