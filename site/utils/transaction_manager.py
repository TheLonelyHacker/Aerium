"""
Database Transaction Manager
Handles transactions and rollback logic for multi-step database operations
"""

from contextlib import contextmanager
from database import get_db
from flask import current_app
from typing import Callable, Any
import logging


@contextmanager
def db_transaction(name: str = "unnamed"):
    """
    Context manager for database transactions with automatic rollback on error
    
    Usage:
        with db_transaction("user_creation"):
            user = create_user(...)
            set_user_role(user.id, 'admin')
            # If any error occurs, both operations are rolled back
    
    Args:
        name: Name of transaction for logging
    
    Yields:
        Database connection with transaction support
    """
    db = get_db()
    try:
        db.execute("BEGIN")
        yield db
        db.commit()
        logger = current_app.logger if current_app else None
        if logger:
            logger.debug(f"Transaction '{name}' committed successfully")
    except Exception as e:
        db.rollback()
        logger = current_app.logger if current_app else None
        if logger:
            logger.error(f"Transaction '{name}' failed and rolled back: {str(e)}")
        raise
    finally:
        db.close()


@contextmanager
def db_transaction_with_retries(name: str = "unnamed", max_retries: int = 3):
    """
    Context manager for database transactions with automatic retry on failure
    
    Args:
        name: Name of transaction for logging
        max_retries: Maximum retry attempts
    
    Yields:
        Database connection with transaction support
    """
    logger = current_app.logger if current_app else None
    
    for attempt in range(max_retries):
        db = get_db()
        try:
            db.execute("BEGIN")
            yield db
            db.commit()
            if logger:
                logger.debug(f"Transaction '{name}' committed on attempt {attempt + 1}")
            return
        except Exception as e:
            db.rollback()
            db.close()
            
            if attempt == max_retries - 1:
                if logger:
                    logger.error(f"Transaction '{name}' failed after {max_retries} attempts: {str(e)}")
                raise
            else:
                if logger:
                    logger.warning(f"Transaction '{name}' failed on attempt {attempt + 1}, retrying...")


def safe_transaction(operation_name: str):
    """
    Decorator for functions that perform database transactions
    
    Usage:
        @safe_transaction("delete_user")
        def delete_user_and_data(user_id):
            # All operations are wrapped in a transaction
            pass
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            with db_transaction(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def batch_insert(db, table: str, rows: list, batch_size: int = 1000) -> int:
    """
    Efficiently insert multiple rows with transaction support
    
    Args:
        db: Database connection
        table: Table name
        rows: List of dictionaries to insert
        batch_size: Number of rows per batch
    
    Returns:
        Total number of rows inserted
    """
    if not rows:
        return 0
    
    # Build column names from first row
    columns = list(rows[0].keys())
    placeholders = ', '.join(['?' for _ in columns])
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    
    total_inserted = 0
    logger = current_app.logger if current_app else None
    
    try:
        # Process in batches
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            
            for row in batch:
                values = tuple(row.get(col) for col in columns)
                db.execute(sql, values)
            
            db.commit()
            total_inserted += len(batch)
            
            if logger:
                logger.debug(f"Inserted {total_inserted}/{len(rows)} rows")
        
        if logger:
            logger.info(f"Batch insert completed: {total_inserted} rows in {table}")
        
        return total_inserted
    
    except Exception as e:
        db.rollback()
        if logger:
            logger.error(f"Batch insert failed after {total_inserted} rows: {str(e)}")
        raise


def batch_update(db, table: str, updates: list, where_clause: str, batch_size: int = 1000) -> int:
    """
    Efficiently update multiple rows with transaction support
    
    Args:
        db: Database connection
        table: Table name
        updates: List of tuples (values_dict, where_params)
        where_clause: WHERE clause with placeholders
        batch_size: Number of rows per batch
    
    Returns:
        Total number of rows updated
    """
    if not updates:
        return 0
    
    total_updated = 0
    logger = current_app.logger if current_app else None
    
    try:
        # Get first update to build SQL
        if updates:
            first_values = updates[0][0]
            columns = list(first_values.keys())
            set_clause = ', '.join([f"{col} = ?" for col in columns])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            
            # Process in batches
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                
                for values_dict, where_params in batch:
                    values = tuple(values_dict.get(col) for col in columns)
                    params = values + where_params
                    db.execute(sql, params)
                
                db.commit()
                total_updated += len(batch)
                
                if logger:
                    logger.debug(f"Updated {total_updated}/{len(updates)} rows")
        
        if logger:
            logger.info(f"Batch update completed: {total_updated} rows in {table}")
        
        return total_updated
    
    except Exception as e:
        db.rollback()
        if logger:
            logger.error(f"Batch update failed after {total_updated} rows: {str(e)}")
        raise


def batch_delete(db, table: str, ids: list, id_column: str = 'id', batch_size: int = 1000) -> int:
    """
    Efficiently delete multiple rows with transaction support
    
    Args:
        db: Database connection
        table: Table name
        ids: List of IDs to delete
        id_column: Name of ID column
        batch_size: Number of rows per batch
    
    Returns:
        Total number of rows deleted
    """
    if not ids:
        return 0
    
    total_deleted = 0
    logger = current_app.logger if current_app else None
    
    try:
        # Process in batches
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i + batch_size]
            placeholders = ', '.join(['?' for _ in batch])
            sql = f"DELETE FROM {table} WHERE {id_column} IN ({placeholders})"
            
            db.execute(sql, batch)
            db.commit()
            total_deleted += len(batch)
            
            if logger:
                logger.debug(f"Deleted {total_deleted}/{len(ids)} rows")
        
        if logger:
            logger.info(f"Batch delete completed: {total_deleted} rows from {table}")
        
        return total_deleted
    
    except Exception as e:
        db.rollback()
        if logger:
            logger.error(f"Batch delete failed after {total_deleted} rows: {str(e)}")
        raise
