from django.utils import timezone

from log.models import AccessControlLogs, ConflictOfInterestLogs, LoginLog, Severity
from ipware.ipware import IpWare
from staff.models import Staff

from user.models import User

NUMBER_OF_SECONDS_FOR_SESSION = 300 # 5 minutes

def get_ip_address_from_request(request):
        ip, _ = IpWare().get_client_ip(meta=request.META)
        return ip.exploded


class LoginLogger:
    

    def __init__(self, login_type, login_request, login_response=None, user=None):
        self.login_type = login_type
        self.login_request = login_request
        self.login_response = login_response
        self.user = user
        self.log_login_attempt()

    def log_login_attempt(self):
        is_success = False
        if self.login_response != None:
            is_success = self.login_response.status_code == 200
        username = self.login_request.data["username"]
        ip = get_ip_address_from_request(self.login_request)
        logs_by_ip = LoginLog.objects.filter(ip=ip).order_by("-timestamp")
        count = self.get_count(is_success, logs_by_ip)
        logs_by_username = LoginLog.objects.filter(login_type=self.login_type, username=username).order_by("-timestamp")
        severity = self.get_severity(is_success, ip, count, logs_by_username)
        LoginLog.objects.create(login_type=self.login_type, is_success=is_success, username=username, user=self.user, ip=ip, count=count, severity=severity)

    def get_count(self, is_success, logs_by_ip):
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

    def get_severity(self, is_success, ip, count, logs_by_username):
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


class AccessControlLogger:
    def __init__(self, request, api_permission_type, view_name):
        self.request = request
        self.user = request.user
        self.api_permission_type = api_permission_type
        self.view_name = view_name
        self.log_access_control_violation()

    def log_access_control_violation(self):
        user_permission_type = self.user.type
        if user_permission_type == User.user_type.STAFF:
            user_permission_type = Staff.objects.get(user=self.user).title
        user_violation_count = self.get_user_violation_count()
        ip = get_ip_address_from_request(self.request)
        ip_violation_count = self.get_ip_violation_count(ip)
        severity = self.get_severity(user_violation_count, ip_violation_count)
        AccessControlLogs.objects.create(user=self.user, user_permission_type=user_permission_type, user_violation_count=user_violation_count, api_permission_type=self.api_permission_type, api_view_name=self.view_name, ip=ip, ip_violation_count=ip_violation_count, severity=severity)

    def get_user_violation_count(self):
        count = 1
        for log in AccessControlLogs.objects.filter(user=self.user).order_by("-timestamp"):
            count = log.user_violation_count + 1
            break
        return count

    def get_ip_violation_count(self, ip):
        count = 1
        for log in AccessControlLogs.objects.filter(ip=ip).order_by("-timestamp"):
            count = log.ip_violation_count + 1
            break
        return count
    
    def get_severity(self, user_violation_count, ip_violation_count):
        if user_violation_count > 4 or ip_violation_count > 4:
            return Severity.HIGH
        if user_violation_count > 2 or ip_violation_count > 2:
            return Severity.MEDIUM
        return Severity.LOW


class ConflictOfInterestLogger:
    def __init__(self, request, ticket):
        self.log, created = ConflictOfInterestLogs.objects.get_or_create(ticket=ticket)
        self.ip = get_ip_address_from_request(request)
        if created:
            self.populate_customer_details()
        else:
            self.populate_staff_details()
    
    def populate_customer_details(self):
        self.log.customer = self.log.ticket.created_by
        self.log.customer_username = self.log.customer.user.username
        self.log.customer_ip = self.ip
        self.log.save()

    def populate_staff_details(self):
        self.log.staff = self.log.ticket.closed_by
        self.log.staff_username = self.log.staff.user.username
        self.log.staff_ip = self.ip
        self.log.time_to_approve = (self.log.ticket.closed_date - self.log.ticket.created_date).total_seconds()
        self.log.severity = self.get_severity()
        self.log.save()

    def get_severity(self):
        same_username = self.log.customer_username == self.log.staff_username
        same_ip = self.log.customer_ip == self.log.staff_ip

        if same_ip:
            return Severity.HIGH
        if same_username:
            return Severity.MEDIUM
        if self.log.time_to_approve <= NUMBER_OF_SECONDS_FOR_SESSION:
            return Severity.LOW
        return Severity.INFO
