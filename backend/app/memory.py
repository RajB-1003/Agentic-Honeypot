"""
Database initialization and session management.
"""
import os
import sqlite3
from collections import OrderedDict
from datetime import datetime
from typing import Optional, Dict, Any

# Global Session Storage (LRU Cache)
SESSION_STORAGE = OrderedDict()
MAX_SESSIONS = 500
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "threats.db"
)


import sqlite3
import os

# Define the path relative to THIS file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, "../data")
DB_PATH = os.path.join(DB_FOLDER, "threats.db")

def init_db():
    # 1. Create the 'data' folder if it is missing
    if not os.path.exists(DB_FOLDER):
        print(f"Creating: {DB_FOLDER}")
        os.makedirs(DB_FOLDER)

    # 2. Connect (creates the file automatically)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 3. Create Tables (Idempotent - safe to run multiple times)
    # Session Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')

    # Threat Intel Cache (URLs, Emails, Phones)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threat_cache (
            value TEXT PRIMARY KEY,
            type TEXT,
            confidence REAL,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        init_db()
    return sqlite3.connect(DB_PATH)


def check_cache(domain: str) -> Optional[Dict[str, Any]]:
    if not domain:
        return None
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT domain, type, confidence FROM threats WHERE domain = ?",
            (domain,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "domain": row[0],
                "type": row[1],
                "confidence": row[2]
            }
        return None
    except sqlite3.Error:
        return None


def update_cache(domain: str, threat_type: str, confidence: float) -> None:
    """
    Update or insert a threat into the database.

    Args:
        domain (str): The domain identifier.
        threat_type (str): The classification of the threat.
        confidence (float): The confidence score of the detection.
    """
    if not domain:
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO threats (domain, type, confidence, last_seen)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(domain) DO UPDATE SET
                type=excluded.type,
                confidence=excluded.confidence,
                last_seen=excluded.last_seen
        ''', (domain, threat_type, confidence, datetime.now()))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database Update Error: {e}")


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session from LRU cache, moving it to the end."""
    if session_id in SESSION_STORAGE:
        SESSION_STORAGE.move_to_end(session_id)
        return SESSION_STORAGE[session_id]
    return None


def create_session(session_id: str, data: Dict[str, Any]) -> None:
    """Create a new session. Evict oldest if limit reached."""
    if session_id in SESSION_STORAGE:
        SESSION_STORAGE.move_to_end(session_id)
        SESSION_STORAGE[session_id] = data
    else:
        SESSION_STORAGE[session_id] = data
        if len(SESSION_STORAGE) > MAX_SESSIONS:
            SESSION_STORAGE.popitem(last=False)
