import logging
from colorlog import StreamHandler, ColoredFormatter

logging.basicConfig(
            level=logging.DEBUG, 
            format='%(log_color)s[%(asctime)s] [%(levelname)s]: %(message)s%(reset)s', 
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                StreamHandler()
            ]
        )

logging.getLogger().handlers[0].setFormatter(
    ColoredFormatter(
    '%(log_color)s%(bold)s[%(asctime)s] [%(levelname)s]:%(reset)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
    )
)
    