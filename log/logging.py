from django.utils import timezone

from log.models import LoginLog, Severity
from ipware.ipware import IpWare

NUMBER_OF_SECONDS_FOR_SESSION = 300 # 5 minutes

def log_login_attempt(login_type, login_request, login_response=None, user=None):
    is_success = False
    if login_response != None:
        is_success = login_response.status_code == 200
    username = login_request.data["username"]
    ip = get_ip_address_from_request(login_request)
    timestamp = timezone.now()
    logs_by_ip = LoginLog.objects.filter(ip=ip).order_by("-timestamp")
    count = get_count(is_success, logs_by_ip)
    logs_by_username = LoginLog.objects.filter(login_type=login_type, username=username).order_by("-timestamp")
    level = get_level(is_success, ip, count, logs_by_username)
    LoginLog.objects.create(login_type=login_type, is_success=is_success, username=username, user=user, ip=ip, timestamp=timestamp, count=count, level=level)


def get_ip_address_from_request(login_request):
    proxy_count = 11
    ip = None
    while ip == None:
        proxy_count -= 1
        if proxy_count < 0:
            return None
        ipw = IpWare(proxy_count=proxy_count)
        ip, _ = ipw.get_client_ip(meta=login_request.META)
    return ip.exploded


def get_count(is_success, logs_by_ip):
    if is_success:
        return 1
    for log in logs_by_ip:
        # new login session because previous login was successful
        if log.is_success:
            return 1
        # new login session after attempting more than 5 min ago
        time_delta = (timezone.now() - log.timestamp).total_seconds()
        if time_delta > NUMBER_OF_SECONDS_FOR_SESSION:
            return 1
        return log.count + 1
    return 1


def get_level(is_success, ip, count, logs_by_username):
    if is_success:
        return Severity.INFO
    
    for log in logs_by_username:
        time_delta = (timezone.now() - log.timestamp).total_seconds()
        if time_delta <= NUMBER_OF_SECONDS_FOR_SESSION and ip != log.ip:
            return Severity.HIGH
        if count > 4:
            return Severity.HIGH
        if count > 2:
            return Severity.MEDIUM
        return Severity.LOW
    return Severity.LOW