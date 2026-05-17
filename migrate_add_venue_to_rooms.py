"""
Migration script to add venue_id to the room table if it doesn't exist
"""
import mysql.connector
from config import db_config

def migrate():
    try:
        config = db_config()
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = conn.cursor()
        
        # Check if venue_id column exists
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='room' AND COLUMN_NAME='venue_id'
        """)
        
        if cursor.fetchone() is None:
            # Add venue_id column
            cursor.execute("""
                ALTER TABLE room ADD COLUMN venue_id INT,
                ADD FOREIGN KEY (venue_id) REFERENCES venue(id),
                ADD INDEX idx_venue_id (venue_id)
            """)
            conn.commit()
            print("✅ venue_id column added to room table")
        else:
            print("✅ venue_id column already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration error: {e}")

if __name__ == '__main__':
    migrate()
