import logging

db_default_formatter = logging.Formatter()

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from .models import LoginLog, APILog
        print('Test handler')
        print(self)
        print(record)

    def format(self, record):
        fmt = self.formatter
        return fmt.format(record)