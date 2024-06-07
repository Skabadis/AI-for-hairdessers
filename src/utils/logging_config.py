import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# # Ensure the logs directory exists
# if not os.path.exists('logs'):
#     os.makedirs('logs')

# # Create a unique log file name based on the current date and time
# current_time = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
# log_filename = f"logs/call_{current_time}.log"

# # Set up the log handler
# handler = RotatingFileHandler(log_filename, maxBytes=10000, backupCount=10)
# handler.setLevel(logging.INFO)

# # Set up the formatter
# formatter = logging.Formatter(
#     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]', datefmt='%H:%M:%S')
# handler.setFormatter(formatter)

# # Get the root logger and configure it
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logger.addHandler(handler)


def initialize_logger():
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create a unique log file name based on the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    log_filename = f"logs/call_{current_time}.log"

    # Set up the log handler
    handler = RotatingFileHandler(log_filename, maxBytes=10000, backupCount=10)
    handler.setLevel(logging.INFO)

    # Set up the formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)

    # Get the root logger and configure it
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove all old handlers to prevent duplicate logs
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    logger.addHandler(handler)
