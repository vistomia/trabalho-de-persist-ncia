import logging
import time
from colorlog import StreamHandler, ColoredFormatter

logging.basicConfig(
            level=logging.INFO, 
            format='%(log_color)s[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s%(reset)s', 
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                StreamHandler()
            ]
        )

logging.getLogger().handlers[0].setFormatter(
    ColoredFormatter(
        '%(log_color)s%(bold)s[%(asctime)s] [%(levelname)s] [%(name)s]:%(reset)s %(message)s',
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

async def middle_logger(request, response, process_time):
    method_colors = {
        "GET": "\033[92m",     # Verde
        "POST": "\033[94m",    # Azul
        "PUT": "\033[93m",     # Amarelo
        "PATCH": "\033[95m",   # Magenta
        "DELETE": "\033[91m",  # Vermelho
        "HEAD": "\033[96m",    # Ciano
        "OPTIONS": "\033[97m"  # Branco
    }
    reset_color = "\033[0m"
    
    method_color = method_colors.get(request.method, "\033[0m")

    return f"{request.client.host} - {method_color}{request.method}{reset_color} {request.url.path} {response.status_code} - {process_time:.4f}s"

