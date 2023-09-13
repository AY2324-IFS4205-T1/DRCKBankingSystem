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

from customer.views import ApplyView, CustomerRegistrationView, CustomerLoginView, GetAccountTypesView, GetBalanceView
from staff.views import ApproveView, GetClosedTicketsView, GetOpenTicketsView, RejectView, StaffLoginView, StaffRegistrationView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # Customer
    path("customer/register", CustomerRegistrationView.as_view(), name="customerRegister"),
    path("customer/login", CustomerLoginView.as_view(), name="customerLogin"),
    path("customer/get_account_types", GetAccountTypesView.as_view(),name="customerGetAccountTypes",),
    path("customer/apply", ApplyView.as_view(), name="apply"),
    path("customer/balance", GetBalanceView.as_view(), name="balance"),

    # Staff
    path('staff/register', StaffRegistrationView.as_view(), name='staffRegister'),
    path("staff/login", StaffLoginView.as_view(), name="staffLogin"),
    path("staff/approve", ApproveView.as_view(), name="approve"),
    path("staff/reject", RejectView.as_view(), name="reject"),
    path("staff/get_open_tickets", GetOpenTicketsView.as_view(), name="get_open_tickets"),
    path("staff/get_closed_tickets", GetClosedTicketsView.as_view(), name="get_closed_tickets"),

    # In logout, header key: Authorization, Value: Token 3510ff361b..
    path("logout", knox_views.LogoutView.as_view(), name="logout"),
]
