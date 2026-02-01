#!/usr/bin/env python3
"""
Initialize Y2MA Database
Creates SQLite database tables for analytics and metrics.
"""

import sqlite3
from pathlib import Path


def init_database(db_path: str = None):
    """Initialize the SQLite database with required tables"""
    
    if db_path is None:
        db_path = Path(__file__).parent.parent / "data" / "analytics.db"
    else:
        db_path = Path(db_path)
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Initializing database at: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Queries table
    print("  Creating queries table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            query_text TEXT,
            intent TEXT,
            num_chunks_retrieved INTEGER,
            avg_retrieval_score REAL,
            response_length INTEGER,
            model_used TEXT,
            total_tokens INTEGER,
            latency_ms INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Feedback table
    print("  Creating feedback table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id INTEGER,
            rating INTEGER,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (query_id) REFERENCES queries(id)
        )
    """)
    
    # Security events table
    print("  Creating security_events table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            event_type TEXT,
            severity TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sessions table
    print("  Creating sessions table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0,
            metadata TEXT
        )
    """)
    
    # Create indexes
    print("  Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_session ON queries(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_events(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_id ON sessions(session_id)")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database initialized successfully at {db_path}")
    print(f"   Tables: queries, feedback, security_events, sessions")


if __name__ == "__main__":
    init_database()
