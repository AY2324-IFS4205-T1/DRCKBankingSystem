import json
import random
import string
from datetime import datetime, timedelta, timezone
from user.models import User
from customer.models import AccountTypes, Accounts
from django.utils import timezone
import subprocess
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password
import os

TRANSACTIONS_MODEL = "customer.Transactions"


def get_userids():
    """
    Retrieves all user_ids of exisiting Customers in database
    """
    user_ids = list(User.objects.filter(type='Customer').values_list('id', flat=True))
    return user_ids


def get_random_birthdate():
    start_date = datetime(1940, 1, 1)
    end_date = datetime.now()
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    formatted_date = make_aware(random_date).strftime("%Y-%m-%d")
    return formatted_date


def get_random_identity_number(): 
    """
    Generates random identity number based on regex='^[STFG]\d{7}[A-Z]$'
    """
    first_char = random.choice("STFGM")
    digits = ''.join(random.choices(string.digits, k=7))
    last_char = random.choice(string.ascii_uppercase)
    identity_no = f"{first_char}{digits}{last_char}"
    return identity_no


def get_random_postal_code():
    six_digit_number = random.randint(100000, 999999)
    return str(six_digit_number)


def get_random_citizenship():
    # List of possible nationalities
    nationalities = ["Singaporean Citizen", "Singaporean PR", "Non-Singaporean"]
    random_nationality = random.choice(nationalities)
    return random_nationality


def get_random_datetime():
    """
    Assumes that the earliest transaction is made in 1990. Generates a random datetime in 
    accepted format by database
    """
    now = datetime.utcnow()

    start_year = 1990 # Assume we are a new-ish bank
    
    end_year = now.year
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
    formatted_datetime = choose_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return formatted_datetime


def get_random_gender():
    genders = ["Male", "Female"]
    return random.choice(genders)


def get_random_account_type():
    """
    Retrieves all account types from database and randomly chooses one
    """
    types = list(AccountTypes.objects.values_list('type', flat=True))
    return random.choice(types)


def get_random_balance():
    balance = random.randint(1, 999999)
    return str(balance)


def get_random_account_id(check):
    """
    Generates a random account id for Transactions table. 

    Parameters
    ----------
    check == 0 when transaction made is either Deposit or Withdrawal, where only one account_id is required
    for the entry. 
    check == sender_account when transaction is a Transfer. Second account_id generate will have to be different
    from sender_account
    
    """
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
    """
    Retrieves balance of sender from database. Transaction amount is less than or equals to balance.
    Function will not deduct the amount from the sender
    """
    s = Accounts.objects.get(account=sender_id)
    balance = float(s.balance)
    random_amount = round(random.uniform(1, balance), 2)
    return random_amount


def get_random_transaction_type():
    transaction_types = ["Deposit", "Withdrawal", "Transfer"]
    return random.choice(transaction_types)


def generate_random_password(length=15):
    """
    Generates a random string of minimum length 12 and default length of 15
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    length = max(length, 12)
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


# Functions for Generation of Dataset in Customer Schema
def generate_auth_user(num_users):
    """
    Generates customers in auth_user table. Primary key is incremented automatically so it is excluded from function
    """
    data = []
    for i in range(1, num_users + 1):
        username = f"test{i}"
        hash_password = make_password(generate_random_password())
        user_data = {
            "pk": i,
            "model": "user.user",
            "fields": {
                "username": username,
                "password": hash_password,
                "phone_no": "12345678",
                "type": "Customer",
                "email": f"{username}@gmail.com",
                "date_joined": get_random_datetime(),
                "last_login": get_random_datetime()
            }
        }
        data.append(user_data)

    with open("generate_data/fixtures/auth_users.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


def generate_customer():
    user_ids = get_userids()
    data = []

    for i, user_id in enumerate(user_ids):
        user_data = {
            "pk": user_id, 
            "model": "customer.Customer",
            "fields": {
                "user": str(user_id),
                "first_name": f"test{i+1}",
                "last_name": f"lastname{i+1}",
                "birth_date": get_random_birthdate(),
                "identity_no": get_random_identity_number(),
                "address": "address",
                "postal_code": get_random_postal_code(),
                "citizenship": get_random_citizenship(),
                "gender": get_random_gender()
            }
        }
        data.append(user_data)
    with open("generate_data/fixtures/customers.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

def generate_account():
    user_ids = get_userids()
    data = []
    for _,user_id in enumerate(user_ids):
        user_data = {
            "model": "customer.Accounts",
            "fields": {
                "user": str(user_id),
                "type": get_random_account_type(),
                "balance": get_random_balance(),
                # Write a function to get different kind of status
                "status": "Active",
                "date_created": get_random_datetime()
            }
        }
        data.append(user_data)

    with open("generate_data/fixtures/accounts.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


def deposit_entry():
    recipient_account = get_random_account_id(0)
    balance = get_random_balance()
    user_data = {
            "model": TRANSACTIONS_MODEL,
            "fields": {
                "transaction_type": "Deposit",
                "recipient": str(recipient_account),
                "description": "NA",
                "amount": str(balance),
                "date": get_random_datetime()
            }
        }
    return user_data

def withdrawal_entry():
    sender_account = get_random_account_id(0)
    balance = get_random_balance()
    user_data = {
            "model": TRANSACTIONS_MODEL,
            "fields": {
                "transaction_type": "Withdrawal",
                "sender": str(sender_account),
                "description": "NA",
                "amount": str(balance),
                "date": get_random_datetime()
            }
        }
    return user_data

def transfer_entry():
    sender_account = get_random_account_id(0)
    recipient_account = get_random_account_id(sender_account)
    balance = get_random_balance()
    user_data = {
            "model": TRANSACTIONS_MODEL,
            "fields": {
                "transaction_type": "Transfer",
                "sender": str(sender_account),
                "recipient": str(recipient_account),
                "description": "NA",
                "amount": str(balance),
                "date": get_random_datetime()
            }
        }
    return user_data

def generate_transaction(num_transactions):
    
    data = []

    for _ in range(1, num_transactions + 1):
        transaction_type = get_random_transaction_type()
        
        if transaction_type == "Deposit":
            entry = deposit_entry()
        elif transaction_type == "Withdrawal":
            entry = withdrawal_entry()
        else: # Transfers constraint -> cannot send to own account
            entry = transfer_entry()
        data.append(entry)
    with open("generate_data/fixtures/transactions.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


def load_data(fixture_file):
    """
    Runs command to load data from fixtures into database
    """
    command = ["python", "manage.py", "loaddata", str(fixture_file)]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")



# Main Function
# Define number of users you want to generate
generate_auth_user(30)
load_data("generate_data/fixtures/auth_users.json")

generate_customer()
load_data("generate_data/fixtures/customers.json")

if not AccountTypes.objects.exists():
    load_data("generate_data/fixtures/account_types.json")

generate_account()
load_data("generate_data/fixtures/accounts.json")

# # Define number of transactions you want to generate
generate_transaction(300)
load_data("generate_data/fixtures/transactions.json")

print("Customer schema is populated!")

print("Exported JSON!")