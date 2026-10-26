import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

class AppLog:
    @staticmethod
    def setup(filename="quiz_game.log"):
        logging.basicConfig(
            filename=filename,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

    @staticmethod
    def get(name):
        return logging.getLogger(name)

    @staticmethod
    def setup_web(filename="quiz_web.log"):
        """Keep web logs bounded without reconfiguring terminal/root logging."""
        logger = logging.getLogger("quiz.web")
        logger.setLevel(logging.INFO)
        if filename is None:
            return
        path = str(Path(filename).resolve())
        if any(getattr(handler, "baseFilename", None) == path for handler in logger.handlers):
            return
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        try:
            handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        except OSError:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.warning("Log file unavailable; writing logs to stderr", exc_info=True)
        else:
            handler.setFormatter(formatter)
            logger.addHandler(handler)
