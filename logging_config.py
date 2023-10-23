import logging.config
from pathlib import Path

Path("./logs").mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "folder": "logs",
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(message)s",
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "json_ensure_ascii": False,
        },
        "precise": {
            "format": "%(asctime)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "precise",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "encoding": "utf-8",
            "filename": "logs/application.log",
            "maxBytes": 5 * 10**7,
            "backupCount": 3,
        },
    },
    "loggers": {"": {"handlers": ["stdout", "file"], "level": "DEBUG"}},
}

logging.config.dictConfig(LOGGING)


def debug_http():
    import http.client

    httpclient_logger = logging.getLogger("http.client")

    def debug_httpclient(level=logging.DEBUG):
        """Enable HTTPConnection debug logging to the logging framework"""

        def httpclient_log(*args):
            httpclient_logger.log(level, " ".join(args))

        # mask the print() built-in in the http.client module to use
        # logging instead
        http.client.print = httpclient_log
        # enable debugging
        http.client.HTTPConnection.debuglevel = 1

    debug_httpclient()
