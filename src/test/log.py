import logging
from datetime import datetime

# Function to create a logger with a specific name and file
def create_logger(name):
    # Generate a timestamped log file name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Format: YYYYMMDD_HHMMSS
    log_file_name = f'{name}_{timestamp}.log'  # Create log file name

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set log level

    # Create a file handler
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)  # Set level for file handler

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger

# Create multiple loggers
logger1 = create_logger('logger1')
logger2 = create_logger('logger2')

# Example log messages
logger1.info('This is an info message from logger1.')
logger1.warning('This is a warning message from logger1.')
logger1.error('This is an error message from logger1.')

logger2.info('This is an info message from logger2.')
logger2.warning('This is a warning message from logger2.')
logger2.error('This is an error message from logger2.')
