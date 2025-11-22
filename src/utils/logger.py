import logging
import logging.handlers
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

LOG_LEVEL = logging.DEBUG  # Change to INFO for production
LOG_DIR = Path("logs")
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


# ============================================================================
# LOGGER SETUP
# ============================================================================

def setup_logging() -> None:
    """
    Configure the root logger with handlers and formatters.
    
    This sets up:
    - File handler with daily rotation (keeps 30 days of logs)
    - Console handler for immediate feedback during development
    - Different log levels for file (DEBUG) vs console (INFO)
    
    The function is called automatically when the module is imported,
    ensuring consistent logging configuration across the application.
    """
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True)
    
    # Get root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Clear existing handlers to avoid duplicates
    # (important when module is reloaded or in tests)
    root_logger.handlers.clear()
    
    # ========================================
    # File Handler (with rotation)
    # ========================================
    log_file = LOG_DIR / "payment_system.log"
    
    # Rotate logs daily at midnight, keep 30 days
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',        # Rotate at midnight
        interval=1,             # Every 1 day
        backupCount=30,         # Keep 30 days of logs
        encoding='utf-8'        # Support unicode characters
    )
    file_handler.setLevel(LOG_LEVEL)
    
    # Create formatter and attach to handler
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Add handler to root logger
    root_logger.addHandler(file_handler)
    
    # ========================================
    # Console Handler (for development)
    # ========================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Less verbose than file
    
    # Use shorter time format for console readability
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
	"""
	Get a logger instance for a specific module.
	
	Args:
		name: Logger name (usually __name__ of the calling module)
		
	Returns:
		Configured logger instance
	"""
	return logging.getLogger(name)


# ============================================================================
# INITIALIZATION
# ============================================================================

# Setup logging when module is imported
setup_logging()

# Create module logger
logger = get_logger(__name__)
logger.info("Logging system initialized")
