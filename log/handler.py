import logging

db_default_formatter = logging.Formatter()

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from .models import LoginLog
        LoginLog.objects.create(
            level=record.level,
            username=record.user,
            is_success=record.is_success,
            ip=record.ip
        )

    def format(self, record):
        fmt = self.formatter
        return fmt.format(record)