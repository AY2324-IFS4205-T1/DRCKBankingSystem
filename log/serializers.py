from rest_framework import serializers
from log.models import AccessControlLogs, ConflictOfInterestLogs, LoginLog

from log.validations import validate_datetimes, validate_log_id, validate_severity


class LoginLoggingSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.severity = validate_severity(self.json_dict)
        self.start_time, self.end_time = validate_datetimes(self.json_dict)
        return super().validate(attrs)

    def get_logs(self):
        logs = LoginLog.objects.filter(timestamp__gte=self.start_time, timestamp__lte=self.end_time).reverse()
        if self.severity != None:
            logs= logs.filter(severity=self.severity)
        return list(logs.values())[:100]


class AccessControlLoggingSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.severity = validate_severity(self.json_dict)
        self.start_time, self.end_time = validate_datetimes(self.json_dict)
        return super().validate(attrs)

    def get_logs(self):
        logs = AccessControlLogs.objects.filter(timestamp__gte=self.start_time, timestamp__lte=self.end_time).reverse()
        if self.severity != None:
            logs = logs.filter(severity=self.severity)
        return list(logs.values())[:100]



class ConflictOfInterestLoggingSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.severity = validate_severity(self.json_dict)
        self.log_id = validate_log_id(self.json_dict)
        return super().validate(attrs)

    def get_logs(self):
        logs = ConflictOfInterestLogs.objects.all().reverse()
        logs = logs[:self.log_id]
        if self.severity != None:
            logs = logs.filter(severity=self.severity)
        return list(logs.values())[:100]
