from scipy.spatial import distance as dist

import logging

# Configure logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def mouth_aspect_ratio(mouth):
    """
    Calculate the mouth aspect ratio based on the coordinates of the mouth points.

    Parameters:
        mouth (List[Tuple[int, int]]): A list of tuples representing the coordinates of the mouth points.

    Returns:
        float: The mouth aspect ratio.

    """
    try:
        A = dist.euclidean(mouth[2], mouth[9])
        B = dist.euclidean(mouth[4], mouth[7])
        C = dist.euclidean(mouth[0], mouth[6])
        mar = (A + B) / (2.0 * C)
        return mar
    except Exception as e:
        logger.exception("Unhandled exception in mouth_aspect_ratio: %s", str(e))
        raise
