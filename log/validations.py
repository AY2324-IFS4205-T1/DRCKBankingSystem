from rest_framework.serializers import ValidationError
from datetime import datetime, timedelta

from log.models import Severity
from django.utils import timezone

def validate_severity(json_dict):
    try:
        severity = json_dict["severity"]
    except KeyError:
        return None
    if severity not in Severity.values:
        return None
    return severity


def validate_datetimes(json_dict):
    try:
        start_time = json_dict["start"]
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        start_time = timezone.make_aware(start_time)
    except Exception:
        start_time = timezone.now() - timedelta(days=1)
 
    try:
        end_time = json_dict["end"]
        end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
        end_time = timezone.make_aware(end_time)
    except Exception:
        end_time = timezone.now()

    if end_time > timezone.now():
        end_time = timezone.now()

    if start_time >= end_time:
        raise ValidationError("Start time must be before end time.")

    return start_time, end_time
