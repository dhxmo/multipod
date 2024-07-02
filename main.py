from core.util import logger
from gui.MultiPodGUI import MultiPodGUI


def run():
    # STEP 1: check if internet connected. if not, message prompt for network connection

    # STEP 2: check valid user. check signing key and MAC address
    #  TODO: generate keys
    # tab in db -> name, email, phone number, total count, key, mac address
    # https://www.phind.com/search?cache=kafp55arby9xy5cdeedszt5w
    # https://www.kamatera.com/pricing/

    # STEP 3: if valid user -> run
    MultiPodGUI()


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception("Unhandled exception in main: %s", str(e))
