from rest_framework import serializers
from log.models import LoginLog

from log.validations import validate_datetimes, validate_severity


class LoggingSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.severity = validate_severity(self.json_dict)
        self.start_time, self.end_time = validate_datetimes(self.json_dict)
        return super().validate(attrs)

    def get_login_logs(self):
        logs = LoginLog.objects.filter(timestamp__gte=self.start_time, timestamp__lte=self.end_time)
        if self.severity != None:
            logs.filter(level=self.severity)
        return list(logs)

