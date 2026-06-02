import logging
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT_DIR / "logs"


def setup_file_logger(name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = True

    log_path = LOG_DIR / filename
    if not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == log_path
        for handler in logger.handlers
    ):
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(handler)

    return logger
