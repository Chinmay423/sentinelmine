import logging
import json
import time
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

from .config import settings

# Custom JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add request_id if it exists
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
        
        # Add user_id if it exists
        if hasattr(record, 'user_id'):
            log_record["user_id"] = record.user_id
        
        # Add exception info if it exists
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields if they exist
        if hasattr(record, 'extra') and record.extra:
            log_record.update(record.extra)
        
        return json.dumps(log_record)

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up structured logging with file and console handlers
    """
    # Create logger
    logger = logging.getLogger("sentinel")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    logger.propagate = False
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    json_formatter = JSONFormatter()
    
    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # File handler for production
    if settings.API_ENV != "development" or log_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_path = log_file if log_file else log_dir / f"sentinel_{settings.API_ENV}.log"
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    
    return logger

class RequestIdFilter(logging.Filter):
    """
    Logging filter that adds request_id to log records
    """
    def __init__(self, request_id: str = None):
        super().__init__()
        self.request_id = request_id or str(uuid.uuid4())
    
    def filter(self, record):
        record.request_id = self.request_id
        return True

class UserIdFilter(logging.Filter):
    """
    Logging filter that adds user_id to log records
    """
    def __init__(self, user_id: str = None):
        super().__init__()
        self.user_id = user_id
    
    def filter(self, record):
        if self.user_id:
            record.user_id = self.user_id
        return True

def get_request_logger(request_id: str = None, user_id: str = None) -> logging.Logger:
    """
    Get a logger with request context
    """
    logger = logging.getLogger("sentinel")
    
    # Add filters
    request_filter = RequestIdFilter(request_id)
    user_filter = UserIdFilter(user_id)
    
    # Remove old filters
    for handler in logger.handlers:
        for filter_ in handler.filters:
            if isinstance(filter_, (RequestIdFilter, UserIdFilter)):
                handler.removeFilter(filter_)
        
        # Add new filters
        handler.addFilter(request_filter)
        handler.addFilter(user_filter)
    
    return logger 