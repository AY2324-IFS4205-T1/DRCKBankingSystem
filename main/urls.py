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
from django.contrib import admin
from django.urls import path
from knox import views as knox_views

from customer.views import (ApplyView, CustomerLoginView, CustomerWelcomeView, TransactionsView,
                            CustomerRegistrationView, DepositView,
                            AccountTypesView, AccountsView, GetCustomerTicketsView, TransferView,
                            WithdrawView)
from staff.views import (ApproveView, GetClosedTicketsView, GetOpenTicketsView, TicketDetailsView,
                         RejectView, StaffLoginView, StaffRegistrationView)

from user.views import AuthenticationTypeCheckView

urlpatterns = [
    # path('admin/', admin.site.urls),
  
    # Customer
    path("customer/register", CustomerRegistrationView.as_view(), name="customerRegister"),
    path("customer/login", CustomerLoginView.as_view(), name="customerLogin"),
    path("customer/welcome", CustomerWelcomeView.as_view(), name="customerWelcome"),
    path("customer/account_types", AccountTypesView.as_view(), name="customerAccountTypes",),
    path("customer/account/<acct_id>", TransactionsView.as_view(), name="customerAccount"),
    path("customer/apply", ApplyView.as_view(), name="apply"),
    path("customer/get_tickets", GetCustomerTicketsView.as_view(), name="getCustomerTickets"),
    path("customer/accounts", AccountsView.as_view(), name="customerAccounts"),
    path("customer/deposit", DepositView.as_view(), name="deposit"),
    path("customer/withdraw", WithdrawView.as_view(), name="withdraw"),
    path("customer/transfer", TransferView.as_view(), name="transfer"),

    # Staff
    path('staff/register', StaffRegistrationView.as_view(), name='staffRegister'),
    path("staff/login", StaffLoginView.as_view(), name="staffLogin"),
    path("staff/approve", ApproveView.as_view(), name="approve"),
    path("staff/reject", RejectView.as_view(), name="reject"),
    path("staff/get_open_tickets", GetOpenTicketsView.as_view(), name="getOpenTickets"),
    path("staff/get_closed_tickets", GetClosedTicketsView.as_view(), name="getClosedTickets"),
    path("staff/ticket_details", TicketDetailsView.as_view(), name="ticketDetails"),

    #In logout, header key: Authorization, Value: Token 3510ff361b..
    path('logout', knox_views.LogoutView.as_view(), name='logout'),

    path('auth_check', AuthenticationTypeCheckView.as_view(), name='auth_check'),
]
