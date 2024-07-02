from core.util import logger
from gui.MultiPodGUI import MultiPodGUI

#  TODO: generate keys
# tab in db -> name, email, phone number, total count, key, mac address
# https://www.phind.com/search?cache=kafp55arby9xy5cdeedszt5w
# https://www.kamatera.com/pricing/

if __name__ == "__main__":
    try:
        MultiPodGUI()
    except Exception as e:
        logger.exception("Unhandled exception in main: %s", str(e))
