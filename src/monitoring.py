"""
Monitoring and Logging Module
Structured logging, metrics collection, and database initialization
"""

import os
import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import sqlite3

logger = logging.getLogger(__name__)


def setup_logging(
    log_dir: str = None,
    log_level: str = None,
    app_name: str = "y2ma"
):
    """
    Set up structured logging with rotation.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARN, ERROR)
        app_name: Application name for log files
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / "logs"
    else:
        log_dir = Path(log_dir)
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Get numeric level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # JSON formatter for structured logging
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage()
            }
            if hasattr(record, 'context'):
                log_entry['context'] = record.context
            if record.exc_info:
                log_entry['exception'] = self.formatException(record.exc_info)
            return json.dumps(log_entry)
    
    json_formatter = JSONFormatter()
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = log_dir / f"{app_name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=7
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(numeric_level)
    root_logger.addHandler(file_handler)
    
    # JSON log file for analytics
    json_log_file = log_dir / f"{app_name}_json.log"
    json_handler = logging.handlers.RotatingFileHandler(
        json_log_file,
        maxBytes=10*1024*1024,
        backupCount=7
    )
    json_handler.setFormatter(json_formatter)
    json_handler.setLevel(logging.INFO)
    root_logger.addHandler(json_handler)
    
    logger.info(f"Logging configured: level={log_level}, dir={log_dir}")


def log_query(
    session_id: str,
    query: str,
    response_length: int,
    num_chunks: int,
    latency_ms: int,
    model: str = None,
    **extra
):
    """Log a query with context"""
    query_logger = logging.getLogger('y2ma.queries')
    
    log_record = logging.LogRecord(
        name='y2ma.queries',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=f"Query processed: {query[:50]}...",
        args=(),
        exc_info=None
    )
    log_record.context = {
        'session_id': session_id[:8],
        'query_length': len(query),
        'response_length': response_length,
        'num_chunks': num_chunks,
        'latency_ms': latency_ms,
        'model': model,
        **extra
    }
    
    query_logger.handle(log_record)


def log_security_event(
    session_id: str,
    event_type: str,
    severity: str = 'WARNING',
    details: Dict = None
):
    """Log a security event"""
    security_logger = logging.getLogger('y2ma.security')
    
    level = getattr(logging, severity.upper(), logging.WARNING)
    
    log_record = logging.LogRecord(
        name='y2ma.security',
        level=level,
        pathname='',
        lineno=0,
        msg=f"Security event: {event_type}",
        args=(),
        exc_info=None
    )
    log_record.context = {
        'session_id': session_id[:8] if session_id else 'unknown',
        'event_type': event_type,
        'severity': severity,
        'details': details or {}
    }
    
    security_logger.handle(log_record)


class MetricsCollector:
    """Collect and store metrics in SQLite"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "analytics.db"
        
        self.db_path = str(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Queries table
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
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_session ON queries(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_events(timestamp)")
        
        conn.commit()
        conn.close()
    
    def record_query(
        self,
        session_id: str,
        query_text: str,
        num_chunks: int = 0,
        avg_score: float = 0.0,
        response_length: int = 0,
        model: str = None,
        tokens: int = 0,
        latency_ms: int = 0,
        intent: str = None
    ) -> int:
        """Record a query to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO queries (
                session_id, query_text, intent, num_chunks_retrieved,
                avg_retrieval_score, response_length, model_used,
                total_tokens, latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, query_text[:1000], intent, num_chunks,
            avg_score, response_length, model, tokens, latency_ms
        ))
        
        query_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return query_id
    
    def record_feedback(
        self,
        query_id: int,
        rating: int,
        comment: str = None
    ):
        """Record user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedback (query_id, rating, comment)
            VALUES (?, ?, ?)
        """, (query_id, rating, comment))
        
        conn.commit()
        conn.close()
    
    def record_security_event(
        self,
        session_id: str,
        event_type: str,
        severity: str,
        details: Dict = None
    ):
        """Record a security event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        details_json = json.dumps(details) if details else None
        
        cursor.execute("""
            INSERT INTO security_events (session_id, event_type, severity, details)
            VALUES (?, ?, ?, ?)
        """, (session_id, event_type, severity, details_json))
        
        conn.commit()
        conn.close()
    
    def get_stats(self, hours: int = 24) -> Dict:
        """Get metrics for the last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total queries
        cursor.execute("""
            SELECT COUNT(*) FROM queries 
            WHERE timestamp > datetime('now', ?)
        """, (f'-{hours} hours',))
        total_queries = cursor.fetchone()[0]
        
        # Average latency
        cursor.execute("""
            SELECT AVG(latency_ms) FROM queries 
            WHERE timestamp > datetime('now', ?)
        """, (f'-{hours} hours',))
        avg_latency = cursor.fetchone()[0] or 0
        
        # Security events
        cursor.execute("""
            SELECT COUNT(*) FROM security_events 
            WHERE timestamp > datetime('now', ?)
        """, (f'-{hours} hours',))
        security_events = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_queries': total_queries,
            'avg_latency_ms': round(avg_latency, 2),
            'security_events': security_events,
            'period_hours': hours
        }


if __name__ == "__main__":
    # Test monitoring module
    setup_logging(log_level='DEBUG')
    
    print("Testing monitoring module...")
    
    # Test logging
    logger.info("Test info message")
    logger.warning("Test warning message")
    
    log_query(
        session_id="test123",
        query="What is the salary?",
        response_length=500,
        num_chunks=3,
        latency_ms=1500
    )
    
    log_security_event(
        session_id="test123",
        event_type="injection_attempt",
        severity="WARNING",
        details={"pattern": "ignore_instructions"}
    )
    
    # Test metrics
    metrics = MetricsCollector()
    
    query_id = metrics.record_query(
        session_id="test123",
        query_text="What roles are available?",
        num_chunks=5,
        avg_score=0.85,
        response_length=800,
        latency_ms=2000
    )
    print(f"Recorded query ID: {query_id}")
    
    metrics.record_feedback(query_id, rating=1, comment="Very helpful!")
    
    stats = metrics.get_stats(hours=24)
    print(f"Stats: {stats}")
    
    print("\n✅ Monitoring tests passed!")
