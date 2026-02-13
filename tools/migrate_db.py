#!/usr/bin/env python3
"""
Database migration script for enhanced attendance system
"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dashboard.database import DB_PATH, init_db

def migrate_old_data():
    """Migrate data from old schema to new schema"""
    print("Starting database migration...")
    
    # Backup existing database
    backup_path = DB_PATH.with_suffix('.db.backup')
    if DB_PATH.exists():
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"Created backup: {backup_path}")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if old table exists
    c.execute('''SELECT name FROM sqlite_master 
                WHERE type='table' AND name='attendance_old' ''')
    
    if not c.fetchone():
        # Rename old table
        c.execute('ALTER TABLE attendance RENAME TO attendance_old')
        print("Renamed old attendance table to attendance_old")
    
    conn.close()
    
    # Initialize new schema
    init_db()
    print("Initialized new database schema")
    
    # Migrate data from old table
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get old data
    c.execute('SELECT * FROM attendance_old')
    old_data = c.fetchall()
    
    if old_data:
        print(f"Migrating {len(old_data)} attendance records...")
        
        for row in old_data:
            # Extract old data
            old_id, timestamp, name, camera_id, image_base64 = row
            
            # Create or find student
            student_id = f"LEGACY{old_id}"
            c.execute('''
                INSERT OR IGNORE INTO students (student_id, name, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (student_id, name, timestamp, timestamp))
            
            # Get student internal ID
            c.execute('SELECT id FROM students WHERE student_id = ?', (student_id,))
            student_internal_id = c.fetchone()[0]
            
            # Insert into new attendance table
            c.execute('''
                INSERT INTO attendance (
                    student_id, timestamp, camera_id, image_base64, check_in_type
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (student_internal_id, timestamp, camera_id, image_base64, 'legacy'))
        
        conn.commit()
        print("Data migration completed successfully")
    
    # Drop old table
    c.execute('DROP TABLE attendance_old')
    conn.commit()
    conn.close()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_old_data()
