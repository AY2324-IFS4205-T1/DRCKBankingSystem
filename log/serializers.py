from rest_framework import serializers


class LoggingSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        return super().validate(attrs)

    def get_logs(self):
        return None