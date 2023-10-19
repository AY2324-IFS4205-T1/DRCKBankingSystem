"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from anonymisation.views import (CalculateAnonView, GetAnonDataView, QueryAnonView, SetKValueView, ViewAnonStatsView)
from customer.views import (AccountsView, AccountTypesView, CustomerLoginView,
                            CustomerRegistrationView, CustomerTicketsView,
                            CustomerWelcomeView, DepositView, TransactionsView,
                            TransferView, WithdrawView)

from log.views import AccessControlLoggingView, ConflictOfInterestLoggingView, LoginLoggingView
from staff.views import (ApproveView, GetClosedTicketsView, GetOpenTicketsView,
                         RejectView, StaffLoginView, StaffTicketView, StaffWelcomeView)
from user.views import (AuthenticationCheckView, LogoutView,
                        SetupTwoFactorAuthenticationView,
                        VerifyTwoFactorAuthenticationView)

urlpatterns = [
    # Customer
    path("customer/register", CustomerRegistrationView.as_view(), name="customerRegister"),
    path("customer/login", CustomerLoginView.as_view(), name="customerLogin"),
    path("customer/welcome", CustomerWelcomeView.as_view(), name="customerWelcome"),
    path("customer/accounts", AccountsView.as_view(), name="customerAccounts"),
    path("customer/account_transactions", TransactionsView.as_view(), name="customerTransactions"),
    path("customer/account_types", AccountTypesView.as_view(), name="customerAccountTypes",),
    path("customer/tickets", CustomerTicketsView.as_view(), name="customerTickets"),
    path("customer/deposit", DepositView.as_view(), name="deposit"),
    path("customer/withdraw", WithdrawView.as_view(), name="withdraw"),
    path("customer/transfer", TransferView.as_view(), name="transfer"),

    # Staff
    path("staff/login", StaffLoginView.as_view(), name="staffLogin"),
    path("staff/welcome", StaffWelcomeView.as_view(), name="staffWelcome"),
    path("staff/get_open_tickets", GetOpenTicketsView.as_view(), name="getOpenTickets"),
    path("staff/get_closed_tickets", GetClosedTicketsView.as_view(), name="getClosedTickets"),
    path("staff/ticket_details", StaffTicketView.as_view(), name="ticketDetails"),
    path("staff/approve", ApproveView.as_view(), name="ticketApprove"),
    path("staff/reject", RejectView.as_view(), name="ticketReject"),

    # Token Authentication
    path('logout', LogoutView.as_view(), name='logout'),
    path('auth_check', AuthenticationCheckView.as_view(), name='auth_check'),
    
    # 2 Factor Authentication
    path("setup_2FA", SetupTwoFactorAuthenticationView.as_view(), name="setup_2fa"),
    path("verify_2FA", VerifyTwoFactorAuthenticationView.as_view(), name="verify_2fa"),

    # Anonymisation
    path("staff/calculate_anon", CalculateAnonView.as_view(), name="calculate_anon"),
    path("staff/view_anon_stats", ViewAnonStatsView.as_view(), name="view_anon_stats"),
    path("staff/set_k", SetKValueView.as_view(), name="set_k"),
    path("staff/query_results", QueryAnonView.as_view(), name="query_results"),
    path("staff/get_anon_data", GetAnonDataView.as_view(), name="get_anon_data"),

    # Logging
    path("staff/login_logs", LoginLoggingView.as_view(), name="login_logs"),
    path("staff/access_control_logs", AccessControlLoggingView.as_view(), name="access_control_logs"),
    path("staff/conflict_interest_logs", ConflictOfInterestLoggingView.as_view(), name="conflict_interest_logs"),

]
