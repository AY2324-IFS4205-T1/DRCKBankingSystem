from datetime import datetime, timedelta
import random
import subprocess
from django.db import connection

from customer.models import Accounts, AccountTypes
from user.models import User

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

def get_random_balance():
    balance = random.randint(1, 999999)
    return str(balance)
    

def load_data(fixture_file):
    """
    Runs command to load data from fixtures into database
    """
    command = ["python", "manage.py", "loaddata", str(fixture_file)]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")

def execute_delete_sql():
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE django.auth_user CASCADE;")

def get_userids():
    """
    Retrieves all user_ids of exisiting Customers in database
    """
    user_ids = list(User.objects.filter(type='Customer').values_list('user', flat=True))
    return user_ids