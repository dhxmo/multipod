import logging

from gui.MultiPodGUI import MultiPodGUI

# Configure logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        MultiPodGUI()
    except Exception as e:
        logger.exception("Unhandled exception in main: %s", str(e))