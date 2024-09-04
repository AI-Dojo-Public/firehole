import logging


PROXY_LOG_COLOR = '\033[94m'  # Light Blue
HTTP_LOG_COLOR = '\033[92m'  # Light Green

logger = logging.getLogger('proxy_server')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(PROXY_LOG_COLOR + '[PROXY] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)