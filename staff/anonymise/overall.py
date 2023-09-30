from django.db import models
from customer.models import Transactions, Accounts, Customer
from django.db.models import F, Q, Sum, Count
from staff.anonymise.utils.anonymiser import anonymise
from enum import Enum
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
import json
from decimal import Decimal


MAXIMUM_K_VALUE = 10 # anyhow put


def age_convert(birth_date):
    """
    Calculates age based on birthdate 
    """
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def deposit_format(transaction_data):
    """
    Formats the transaction data into deposit format, where there is no sender data

    TESTING PURPOSES: Remove testing, no need for the variable
    """
    deposit_transactions = list()
    testing = []
    for t in transaction_data:
        recipient_age = age_convert(t.recipient.user.birth_date)
        record = [
            recipient_age,
            t.recipient.user.gender, 
            t.recipient.user.postal_code,
            t.recipient.user.citizenship,
            t.amount,
            t.month,
            t.year
        ]
        testing.append(record)
        record_str = ','.join(map(str, record))
        deposit_transactions.append(record_str)
    return deposit_transactions, testing

def withdrawal_format(transaction_data):
    """
    Formats the transaction data into withdrawal format, where there is no receiver data

    TESTING PURPOSES: Remove testing, no need for the variable
    """
    withdrawal_transactions = list()
    testing = []
    for t in transaction_data:
        sender_age = age_convert(t.sender.user.birth_date)
        record = [
            sender_age,
            t.sender.user.gender, 
            t.sender.user.postal_code,
            t.sender.user.citizenship,
            t.amount,
            t.month,
            t.year
        ]
        testing.append(record)
        record_str = ','.join(map(str, record))
        withdrawal_transactions.append(record_str)
    return withdrawal_transactions, testing

def transfer_format(transaction_data):
    """
    Formats the transaction data into transfer format

    TESTING PURPOSES: Remove testing, no need for the variable
    """
    transfer_transactions = list()
    testing = []
    for t in transaction_data:
        sender_age = age_convert(t.sender.user.birth_date) 
        recipient_age = age_convert(t.recipient.user.birth_date) 
        record = [
            sender_age,
            t.sender.user.gender,
            t.sender.user.postal_code,
            t.sender.user.citizenship,
            recipient_age,
            t.recipient.user.gender,
            t.recipient.user.postal_code,
            t.recipient.user.citizenship,
            t.amount,
            t.month,
            t.year
        ]
        testing.append(record)
        record_str = ','.join(map(str, record))
        transfer_transactions.append(record_str)
    return transfer_transactions, testing


def retrieve_all_transactions(type):
    """
    Retrieves all transaction data from database based on the type specified: Deposit, Withdrawal, Transfer. 
    Data is de-identified. Stores in a list to parse to anonymisation function.
    
    Attributes: ['sender_age'], ['sender_gender'], ['sender_postal_code'], ['sender_citizenship'], 
                ['transaction_amount'], ['recipient_age'], ['recipient_gender'], ['recipient_postal_code'],
                ['recipient_citizenship'], ['month'], ['year']
    
    TESTING PURPOSES: Prints results into file: og_transaction_history.data
    """
    query = Transactions.objects.select_related('sender__user', 'recipient__user').filter(
        Q(sender__account=F('sender__account')) | Q(recipient__account=F('recipient__account')),
        transaction_type=type).select_related('sender__user__user', 'recipient__user__user')
    
    transactions = query.annotate(
        month=ExtractMonth('date'),
        year=ExtractYear('date')
    )

    if type == 'Deposit':
        transaction_data, testing = deposit_format(transactions)
        file_name = "unanon_deposit.data"
    elif type == 'Withdrawal':
        transaction_data, testing = withdrawal_format(transactions)
        file_name = "unanon_withdrawal.data"
    else: # For "Transfers"
        transaction_data, testing = transfer_format(transactions)
        file_name = "unanon_transfer.data"

    file_path = "staff/anonymise/data/" + file_name
    # TESTING PURPOSES: Prints transaction history into file
    with open(file_path, "w") as file:
        for r in testing:
            file.write(", ".join(map(str, r)) + "\n")
    print(f"{str(type)} data (not anonymised) printed to {file_name}")
    return transaction_data


def unanonymised_first_query():
    """
    Query: Average withdrawal amounts of Singaporean citizens for the past 5 years
    Use Case: High level view of average withdrawal amounts for researchers to gain insights on Singaporean 
    spending patterns

    The query is performed on all unanonymised transaction data stored in the database and returns a string of data.

    TESTING PURPOSE: 
        - unfiltered.data: Unanonymised data before query is performed on it
        - unanon_query.data: Unanonymised data after query is performed on it
    """
    # Get the table with age, gender, nationality, address (sender+recipient), transaction amount, month, year
    transactions = Transactions.objects.select_related('sender__user', 'recipient__user').filter(
        Q(sender__account=F('sender__account')) | Q(recipient__account=F('recipient__account')), 
        transaction_type='Withdrawal'
        ).select_related('sender__user__user', 'recipient__user__user')
    
    # For testing purposes, can remove after
    unfiltered_data = []
    for u in transactions:

        extract_year = ExtractYear(u.date)
        sender_age = age_convert(u.sender.user.birth_date)
        unfiltered = [
            sender_age,
            u.sender.user.gender,
            u.sender.user.postal_code,
            u.sender.user.citizenship,
            u.amount,
            extract_year
        ]
        unfiltered_data.append(unfiltered)

    # TESTING PURPOSES: Prints data into file unfiltered.data
    with open("staff/anonymise/data/unfiltered.data", "w") as file:
        for unfiltered in unfiltered_data:
            file.write(", ".join(map(str, unfiltered)) + "\n")
    print("Before query is performed on Unanonymised data: unfiltered.data")
    

    # Filter data based on the past five years and Singaporean citizens
    current_date = datetime.now()
    five_years_ago = current_date.replace(year=current_date.year - 4, month=1, day=1, hour=0, minute=0, second=0)
    formatted_datetime = five_years_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    citizen_yearly_transactions = transactions.filter(
        sender__user__citizenship='Singaporean Citizen', date__gte=formatted_datetime
        )
    group_transactions = citizen_yearly_transactions.annotate(
        year=ExtractYear('date')
    ).values(
        'sender__user__citizenship', 'year'
    ).annotate(
        total_amount=Sum('amount'),
        num_transactions=Count('year')
    ).order_by(
        'year'
    )
 
    data = []
    data_json = []
    all_transactions = list()
    for t in group_transactions:
        avg_amount = round((t['total_amount'] / t['num_transactions']), 2)
        year = t['year']
        record_json = {
            'year': year, 
            'avg_amount': avg_amount
        }
        data_json.append(record_json)
        # TESTING PURPOSES: Can remove record
        record = [
            year,
            avg_amount
        ]
        data.append(record)
        record_str = ','.join(map(str, record))
        all_transactions.append(record_str)
    json_output = json.dumps(data_json, indent=4, cls=DecimalEncoder)

    # TESTING PURPOSE: Prints queried unanonymised data to unanon_query.data
    with open("staff/anonymise/data/unanon_query.data", "w") as file:
        for record in data:
            file.write(", ".join(map(str, record)) + "\n")
    print("Unanonymised first query results printed to unanon_query.data")
    return all_transactions, json_output

class DecimalEncoder(json.JSONEncoder):
    """
    Class for json to recognise decimal
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)
    

def anonymised_first_query(data):
    """
    Query: Average withdrawal amounts of Singaporean citizens for the past 5 years
    Use Case: High level view of average withdrawal amounts for researchers to gain insights on Singaporean 
    spending patterns

    Takes in anonymised data as a dict and performs query on data. Returns the query as a dict for displaying

    Constraints: 
    Will only process records where citizenship == Singaporean Citizen, will not take any records with nationality
    suppressed

    TESTING PURPOSES: Returns yearly_data as dict so that can print
    """

    current_year = date.today().year
    past_five_years = current_year - 5
    citizenship_status = 'Singaporean Citizen'
    citizenship_status = citizenship_status.replace(" ","")

    # Filter the transaction data for Singaporeans in the past 5 years
    filtered_data = [
        d for d in data if(
            d['sender_citizenship'] == citizenship_status and
            int(d['year']) > past_five_years
        )
    ]
    yearly_data = {}

    # Sum of all transactions and total number of transactions
    for t in filtered_data:
        year = t['year']
        amount = float(t['transaction_amount'])

        if year in yearly_data:
            yearly_data[year]['total_amount'] += amount
            yearly_data[year]['transaction_count'] += 1
        else:
            # Create a new entry 
            yearly_data[year] = {
                'total_amount': amount,
                'transaction_count': 1
            }
    
    # Calculate the average amount of transactions
    all_data = []
    for year, data in yearly_data.items():
        total_amount = float(data['total_amount'])
        count = data['transaction_count']

        if count > 0:
            average_amount = round((total_amount / count), 2)
        else: 
            average_amount = 0
        record = {
            'year': year,
            'avg_amount': average_amount
        }
        all_data.append(record)
        yearly_data[year]['avg_amount'] = average_amount
    # Return in correct format for json
    json_data = json.dumps(all_data, indent=4, cls=DecimalEncoder)

    # TESTING PURPOSES: Returns dict to send to function for printing
    return yearly_data, json_data


# For testing purpose
def write_first_anon_query(query_data):
    """
    TESTING PURPOSES: Writes first anonymised query to file anonymised_query.data
    """
    with open("staff/anonymise/data/anonymised_query.data", 'w') as file:

        # Iterate through yearly_data and write each entry to the file
        for year, data in query_data.items():
            average_amount = data['avg_amount']
            file.write(f'{year}, {average_amount}\n')

    print('Data has been written to anonymised_query.data')


class QueryOptions(Enum):
    FIRST = "1"
    SECOND = "2"

class UserInputs():
    def __init__(self, k_value, query):
        self.k_value = k_value
        if query in [option.value for option in QueryOptions]:
            self.query = query
        else:
            raise ValueError("Invalid query option. Choose from '1' or '2'.")

# TESTING PURPOSES: Get rid of this printing to json file
def write_to_json_file(json_data, file_name):
    file_path = "staff/anonymise/data/" + file_name

    with open(file_path, "w") as json_file:
        json_file.write(json_data)
    print(f"JSON data printed to {file_path}")


def user_inputs(k, query):
    """
    Is called by API. Takes in user's input to perform anonymity using k-value and perform query on 
    anonymised data. Performs query on both anonymised data and original data to calculate information 
    loss
    """
    new_input = UserInputs(k, query)

    if new_input.query == "1": # Average withdrawal amount of Singaporeans for the past 5 years
        
        # Retrieve all withdrawal data from database
        withdrawal_history = retrieve_all_transactions('Withdrawal')
        
        # Anonymise the withdrawal data
        anon_withdrawal_data = anonymise(withdrawal_history, k, 'Withdrawal')
        
        # Perform first query on anonymised data
        anon_query_result, anon_json = anonymised_first_query(anon_withdrawal_data)
        write_to_json_file(anon_json, "anon.json")

        # TESTING PURPOSES: Write the first query result to file
        write_first_anon_query(anon_query_result)
        _, unanon_json = unanonymised_first_query()
        write_to_json_file(unanon_json, "unanon.json")
        return {"anonymised": anon_json,
                "unanonymised": unanon_json} ## placeholder for testing of API
        
        
# TESTING PURPOSES: For API Calls
# user_inputs(4, "1")







