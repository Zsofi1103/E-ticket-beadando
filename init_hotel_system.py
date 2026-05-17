#!/usr/bin/env python
"""Initialize hotel booking system tables directly via SQL"""
import sys
import pymysql
from config import db_config

def init_hotel_system():
    """Initialize hotel booking system database tables"""
    try:
        config = db_config()
        
        # Connect to MySQL
        connection = pymysql.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            port=int(config.get('port', 3306))
        )
        
        with connection.cursor() as cursor:
            # Read the SQL file
            with open('init_hotel_system.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Execute all statements
            statements = sql_script.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:  # Skip empty statements
                    print(f"Executing: {statement[:60]}...")
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        print(f"  ⚠️  Warning: {e}")
                        # Continue even if some statements fail
            
            connection.commit()
            print("\n✅ Hotel booking system tables initialized successfully!")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    init_hotel_system()
