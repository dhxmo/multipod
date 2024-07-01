from core.util import logger
from gui.MultiPodGUI import MultiPodGUI

if __name__ == "__main__":
    try:
        MultiPodGUI()
    except Exception as e:
        logger.exception("Unhandled exception in main: %s", str(e))
