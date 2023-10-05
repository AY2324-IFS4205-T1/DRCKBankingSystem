import json
import random
import string
from datetime import datetime, timedelta
from secrets import choice
from uuid import UUID

from django.contrib.auth.hashers import make_password
from django.utils.timezone import make_aware

from customer.models import Accounts, AccountTypes

from generate_data.utils.utility import get_random_datetime, load_data, execute_delete_sql, get_userids, get_random_balance

# Define number of users and number of transactions you want to generate
CUSTOMER_NUM = 50
TRANSACTION_NUM = 100

TRANSACTIONS_MODEL = "customer.Transactions"


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)
      
# Functions for Generation of Dataset in Customer Schema
class GenerateAuthUsers:
    def __init__(self, num_of_users, file_path):
        self.num_of_users = num_of_users
        self.file_path = file_path
    
    def generate_auth_user(self):
        """
        Generates customers in auth_user table. Primary key is incremented automatically so it is excluded from function
        """
        data = []
        for i in range(1, self.num_of_users + 1):
            username = f"test{i}"
            hash_password = make_password(self.generate_random_password())
            user_data = {
                # "pk": i,
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

        with open(self.file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def generate_random_password(self, length=15):
        """
        Generates a random string of minimum length 12 and default length of 15
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        length = max(length, 12)
        password = ''.join(choice(characters) for _ in range(length))
        return password

 
class GenerateCustomers:
    def __init__(self, file_path):
        self.file_path = file_path

    def generate_customer(self):
        user_ids = get_userids()
        data = []

        for i, user_id in enumerate(user_ids):
            user_data = {
                "pk": str(user_id), 
                "model": "customer.Customer",
                "fields": {
                    "user": str(user_id),
                    "first_name": f"test{i+1}",
                    "last_name": f"lastname{i+1}",
                    "birth_date": self.get_random_birthdate(),
                    "identity_no": self.get_random_identity_number(),
                    "address": "address",
                    "postal_code": self.get_random_postal_code(),
                    "citizenship": self.get_random_citizenship(),
                    "gender": self.get_random_gender()
                }
            }
            data.append(user_data)
        with open(self.file_path, "w") as json_file:
            json.dump(data, json_file, indent=4, cls=UUIDEncoder)
    
    def get_random_birthdate(self):
        start_date = datetime(1940, 1, 1)
        end_date = datetime.now()
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        formatted_date = make_aware(random_date).strftime("%Y-%m-%d")
        return formatted_date
    
    def get_random_identity_number(self): 
        """
        Generates random identity number based on regex='^[STFG]\d{7}[A-Z]$'
        """
        first_char = choice("STFGM")
        digits = ''.join(random.choices(string.digits, k=7))
        last_char = choice(string.ascii_uppercase)
        identity_no = f"{first_char}{digits}{last_char}"
        return identity_no
    
    def get_random_postal_code(self):
        six_digit_number = random.randint(100000, 999999)
        return str(six_digit_number)
    
    def get_random_citizenship(self):
        # List of possible nationalities
        nationalities = ["Singaporean Citizen", "Singaporean PR", "Non-Singaporean"]
        random_nationality = choice(nationalities)
        return random_nationality
    
    def get_random_gender(self):
        genders = ["Male", "Female"]
        return choice(genders)

class GenerateAccounts:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def generate_account(self):
        user_ids = get_userids()
        data = []
        for _,user_id in enumerate(user_ids):
            user_data = {
                "model": "customer.Accounts",
                "fields": {
                    "user": str(user_id),
                    "type": self.get_random_account_type(),
                    "balance": get_random_balance(),
                    # Write a function to get different kind of status
                    "status": "Active",
                    "date_created": get_random_datetime()
                }
            }
            data.append(user_data)

        with open(self.file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        
    def get_random_account_type(self):
        """
        Retrieves all account types from database and randomly chooses one
        """
        types = list(AccountTypes.objects.values_list('type', flat=True))
        return choice(types)
    
class GenerateTransactions:
    def __init__(self, num_of_transactions, file_path):
        self.num_of_transactions = num_of_transactions
        self.file_path = file_path


    def generate_transaction(self):
        data = []

        for _ in range(1, self.num_of_transactions + 1):
            transaction_type = self.get_random_transaction_type()
            
            if transaction_type == "Deposit":
                entry = DepositEntry()
            elif transaction_type == "Withdrawal":
                entry = WithdrawalEntry()
            else: # Transfers constraint -> cannot send to own account
                entry = TransferEntry()
            data.append(entry.generate())
        with open(self.file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        
    def get_random_transaction_type(self):
        transaction_types = ["Deposit", "Withdrawal", "Transfer"]
        return choice(transaction_types)

class TransactionEntryBase:
    def generate(self):
        raise NotImplementedError("Subclasses must implement generate method.")
    
    def get_random_account_id(self, check):
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
            return choice(account_id)
        else:
            while True:
                account_id = list(Accounts.objects.values_list('account', flat=True))
                new_account_id = choice(account_id)
                if new_account_id != check:
                    return new_account_id

class DepositEntry(TransactionEntryBase):
    def generate(self):
        recipient_account = self.get_random_account_id(0)
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

class WithdrawalEntry(TransactionEntryBase):
    def generate(self):
        sender_account = self.get_random_account_id(0)
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

class TransferEntry(TransactionEntryBase):
    def generate(self):
        sender_account = self.get_random_account_id(0)
        recipient_account = self.get_random_account_id(sender_account)
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


# Delete all the data in database
print("Clearing database of all data")
execute_delete_sql()

# Main Function
auth_users = GenerateAuthUsers(CUSTOMER_NUM, "generate_data/fixtures/auth_users.json")
auth_users.generate_auth_user()

print(f"Loading {CUSTOMER_NUM} Users data into django.auth_user table")
load_data(auth_users.file_path)

customers = GenerateCustomers("generate_data/fixtures/customers.json")
customers.generate_customer()

print(f"Loading {CUSTOMER_NUM} Customer data into customer.customer_info table")
load_data(customers.file_path)

if not AccountTypes.objects.exists():
    print("Loading Account Types data into customer.account_types table")
    load_data("generate_data/fixtures/account_types.json")

accounts = GenerateAccounts("generate_data/fixtures/accounts.json")
accounts.generate_account()

print(f"Loading {CUSTOMER_NUM} Account data into customer.accounts table")
load_data(accounts.file_path)

# Define number of transactions you want to generate
transactions = GenerateTransactions(TRANSACTION_NUM, "generate_data/fixtures/transactions.json")
transactions.generate_transaction()

print(f"Loading {TRANSACTION_NUM} Transaction data into customer.transactions table")
load_data(transactions.file_path)

print("Customer schema is populated!")

print("Exported JSON!")