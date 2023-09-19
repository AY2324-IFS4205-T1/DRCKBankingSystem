import json
import random
import string
from datetime import datetime, timedelta, timezone
from user.models import User
from customer.models import AccountTypes, Accounts
from django.utils import timezone
import subprocess
from django.utils.timezone import make_aware
import pytz

# Global variables
start_date = datetime(1920, 1, 1)
end_date = datetime.now()


def get_userids():
    user_ids = list(User.objects.filter(type='C').values_list('id', flat=True))
    # print(user_ids)
    return user_ids


def get_random_birthdate():
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    # print(type(random_date))
    formatted_date = make_aware(random_date).strftime("%Y-%m-%d")
    return formatted_date


def get_random_identity_number(): #based of: regex='^[STFG]\d{7}[A-Z]$'
    first_char = random.choice("STFG")
    digits = ''.join(random.choices(string.digits, k=7))
    last_char = random.choice(string.ascii_uppercase)
    identity_no = f"{first_char}{digits}{last_char}"
    return identity_no


def get_random_address():
    six_digit_number = random.randint(100000, 999999)
    return str(six_digit_number)


def get_random_nationality():
    # List of possible nationalities
    nationalities = ["Chinese", "Malay", "Indian", "France", "Germany", "Iceland", "Denmark", "Netherlands", "Norway", "Japanese", "Korean"]
    random_nationality = random.choice(nationalities)
    return random_nationality


def get_random_datetime():
    now = datetime.utcnow()

    start_year = 1990
    end_year = now.year
    # print(end_year)

    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    # Months have different days 
    if month == 2:
        day = random.randint(1, 28) # i am NOT doing leap years
    elif month == 1 | month == 3 | month == 5 | month == 7 | month == 8 | month == 10 | month == 12:
        day = random.randint(1, 31)
    else: 
        day = random.randint(1, 30) 
    
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    current_datetime = datetime.now()
    new = current_datetime.replace(year, month, day, hour, minute, second)
    choose_datetime = min(current_datetime, new)
    random_datetime = choose_datetime.isoformat()
    return random_datetime


def get_random_gender():
    genders = ["M", "F"]
    return random.choice(genders)

def get_random_account_type():
    types = list(AccountTypes.objects.values_list('type', flat=True))
    return random.choice(types)

def get_random_balance():
    balance = random.randint(1, 999999)
    return str(balance)


def get_random_account_id(check):
    if check == 0:
        account_id = list(Accounts.objects.values_list('account', flat=True))
        return random.choice(account_id)
    else:
        while True:
            account_id = list(Accounts.objects.values_list('account', flat=True))
            new_account_id = random.choice(account_id)
            if new_account_id != check:
                return new_account_id


def get_random_transaction_value(sender_id):
    # Check the sender's balance before generating the random number
    s = Accounts.objects.get(account=sender_id)
    balance = float(s.balance)
    random_amount = round(random.uniform(1, balance), 2)
    return random_amount


# Functions for Generation of Dataset in Customer Schema
def generate_auth_user(num_users):
    data = []
    for i in range(1, num_users + 1):
        username = f"test{i}"
        user_data = {
            "model": "user.User",
            "fields": {
                "username": username,
                "password": "testpassword",
                "phone_no": "12345678",
                "type": "C",
                "email": f"{i}{i}{i}@gmail.com",
                "date_joined": "2023-01-01"
            }
        }
        data.append(user_data)

    with open("fixtures/auth_users.json", "w") as json_file:
        json.dump(data, json_file, indent=4)



def generate_customer():
    user_ids = get_userids()
    data = []

    for i, user_id in enumerate(user_ids):
        user_data = {
            "model": "customer.Customer",
            "fields": {
                "user": str(user_id),
                "first_name": f"test{i+1}",
                "last_name": "bye",
                "birth_date": get_random_birthdate(),
                "identity_no": get_random_identity_number(),
                "address": get_random_address(),
                "nationality": get_random_nationality(),
                "gender": get_random_gender()
            }
        }
        data.append(user_data)
    with open("fixtures/customers.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

def generate_account():
    user_ids = get_userids()
    data = []
    for i,user_id in enumerate(user_ids):
        user_data = {
            "model": "customer.Accounts",
            "fields": {
                "user": str(user_id),
                "type": get_random_account_type(),
                "balance": get_random_balance(),
                "status": "A",
                "date_created": get_random_datetime()
            }
        }
        data.append(user_data)

    with open("fixtures/accounts.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

def generate_transaction(num_transactions):
    user_ids = get_userids()
    data = []

    for i in range(1, num_transactions + 1):
        sender_account = get_random_account_id(0)
        recipient_account = get_random_account_id(sender_account)
        balance = get_random_transaction_value(sender_account)
        user_data = {
            "model": "customer.Transactions",
            "fields": {
                "sender": str(sender_account),
                "recipient": str(recipient_account),
                "description": "",
                "amount": str(balance),
                "date": get_random_datetime()
            }
        }
        data.append(user_data)

    with open("fixtures/transactions.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


def load_data(fixture_file):
    command = ["python", "manage.py", "loaddata", str(fixture_file)]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")


# # Main Function
# # Define number of users you want to generate
generate_auth_user(10)
load_data("fixtures/auth_users.json")

generate_customer()
load_data("fixtures/customers.json")


if not AccountTypes.objects.exists():
    load_data("fixtures/account_types.json")

generate_account()
load_data("fixtures/accounts.json")

# Define number of transactions you want to generate
generate_transaction(75)
load_data("fixtures/transactions.json")

print("Customer schema is populated!")
# get_userids()