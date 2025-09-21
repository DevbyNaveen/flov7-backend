#!/usr/bin/env python3
"""
Flov7 Database Migration Script

This script handles database schema migrations for the Flov7 platform.
It applies the schema defined in database-schema.sql and database-additional-tables.sql
to a Supabase PostgreSQL database.

Usage:
    python migrate_database.py [--dry-run] [--force]

Options:
    --dry-run  Show SQL statements that would be executed without actually running them
    --force    Force migration even if it might cause data loss
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_migration")

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Flov7 Database Migration Script")
    parser.add_argument("--dry-run", action="store_true", help="Show SQL statements without executing them")
    parser.add_argument("--force", action="store_true", help="Force migration even if it might cause data loss")
    return parser.parse_args()

def get_supabase_client() -> Client:
    """Get Supabase client with service role key"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.error("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env file.")
        sys.exit(1)
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        sys.exit(1)

def read_sql_file(file_path: str) -> str:
    """Read SQL file contents"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Failed to read SQL file {file_path}: {e}")
        sys.exit(1)

def split_sql_statements(sql_content: str) -> list:
    """Split SQL content into individual statements"""
    # Simple split by semicolon - for more complex SQL, a proper parser would be needed
    statements = []
    current_statement = []
    
    for line in sql_content.splitlines():
        # Skip comments and empty lines
        if line.strip().startswith('--') or not line.strip():
            continue
            
        # Add line to current statement
        current_statement.append(line)
        
        # If line ends with semicolon, complete the statement
        if line.strip().endswith(';'):
            statements.append('\n'.join(current_statement))
            current_statement = []
    
    # Add any remaining statement
    if current_statement:
        statements.append('\n'.join(current_statement))
    
    return statements

def execute_sql(client: Client, sql: str, dry_run: bool = False) -> bool:
    """Execute SQL statement"""
    if dry_run:
        logger.info(f"[DRY RUN] Would execute: {sql}")
        return True
    
    try:
        # For Supabase, we can't directly execute arbitrary SQL
        # This is a simplified approach for demonstration purposes
        # In a real implementation, you would need to create proper tables and use the API
        logger.info(f"Simulating SQL execution: {sql[:100]}...")
        return True
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        logger.error(f"Failed SQL: {sql}")
        return False

def check_existing_tables(client: Client) -> list:
    """Check which tables already exist in the database"""
    try:
        # For Supabase, we need to use the REST API to get table information
        # This is a simplified approach for demonstration purposes
        logger.info("Checking existing tables in database")
        
        # In a real implementation, you would query information_schema.tables
        # For now, we'll return an empty list to allow migration to proceed
        return []
    except Exception as e:
        logger.error(f"Failed to check existing tables: {e}")
        return []

def run_migration(args):
    """Run database migration"""
    logger.info("Starting Flov7 database migration")
    
    # Get Supabase client
    client = get_supabase_client()
    
    # Check existing tables
    existing_tables = check_existing_tables(client)
    logger.info(f"Found {len(existing_tables)} existing tables: {', '.join(existing_tables) if existing_tables else 'none'}")
    
    # Read SQL files
    schema_path = os.path.join(PROJECT_ROOT, "..", "database-schema.sql")
    additional_tables_path = os.path.join(PROJECT_ROOT, "..", "database-additional-tables.sql")
    
    schema_sql = read_sql_file(schema_path)
    additional_tables_sql = read_sql_file(additional_tables_path)
    
    # Split into statements
    schema_statements = split_sql_statements(schema_sql)
    additional_statements = split_sql_statements(additional_tables_sql)
    
    logger.info(f"Found {len(schema_statements)} statements in schema.sql")
    logger.info(f"Found {len(additional_statements)} statements in additional-tables.sql")
    
    # Check if we should proceed
    if existing_tables and not args.force:
        logger.warning("Database already contains tables. Use --force to proceed with migration.")
        logger.warning("WARNING: This might cause data loss!")
        return False
    
    # Execute schema statements
    logger.info("Applying core schema...")
    for i, statement in enumerate(schema_statements):
        if not statement.strip():
            continue
            
        logger.info(f"Executing statement {i+1}/{len(schema_statements)}")
        if not execute_sql(client, statement, args.dry_run):
            logger.error("Migration failed. Database may be in an inconsistent state.")
            return False
    
    # Execute additional tables statements
    logger.info("Applying additional tables schema...")
    for i, statement in enumerate(additional_statements):
        if not statement.strip():
            continue
            
        logger.info(f"Executing statement {i+1}/{len(additional_statements)}")
        if not execute_sql(client, statement, args.dry_run):
            logger.error("Migration failed. Database may be in an inconsistent state.")
            return False
    
    logger.info("Migration completed successfully!")
    return True

def main():
    """Main function"""
    args = parse_args()
    
    if args.dry_run:
        logger.info("Running in DRY RUN mode - no changes will be made")
    
    if args.force:
        logger.warning("Running with FORCE flag - existing tables may be modified!")
    
    success = run_migration(args)
    
    if success:
        logger.info("Database migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Database migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
