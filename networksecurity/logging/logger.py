import logging
import os
import sys
from datetime import datetime

# Create a timestamp for the log filename
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Create the logs directory
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Create the complete log file path
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Configure logging with both file and console handlers
logging.basicConfig(
    format="[%(asctime)s] %(name)s %(levelname)s line %(lineno)d: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create a reusable logger
logger = logging.getLogger("networksecurity")