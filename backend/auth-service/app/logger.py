import logging
import json
import sys

from app.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


# Создаём логгер
logger = logging.getLogger("app")
logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

# Обработчик логов (в консоль)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)
