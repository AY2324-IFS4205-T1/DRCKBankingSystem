from django.db import models
from customer.models import Transactions, Accounts, Customer
from django.db.models import F, Q, Sum, Count
from staff.anonymise.utils.anonymiser import anonymise
from enum import Enum
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear


MAXIMUM_K_VALUE = 10 # anyhow put


def age_convert(birth_date):
    """
    Calculates age based on birthdate 
    """
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    return age


def retrieve_all_transactions():
    """
    Retrieves all transaction data from database. Stores in a list for anonymisation
    
    Attributes: ['sender_age'], ['sender_gender'], ['sender_address'], ['sender_nationality'], 
                ['transaction_amount'], ['recipient_age'], ['recipient_gender'], ['recipient_address'],
                ['recipient_nationality'], ['month'], ['year']
    
    TESTING: Prints results into file: og_transaction_history.data
    """
    all_transactions = list()
    testing = []
    query = Transactions.objects.select_related('sender__user', 'recipient__user').filter(
        Q(sender__account=F('sender__account')) | Q(recipient__account=F('recipient__account'))
        ).select_related('sender__user__user', 'recipient__user__user')
    transactions = query.annotate(
        month=ExtractMonth('date'),
        year=ExtractYear('date')
    )
    for t in transactions:
        sender_age = age_convert(t.sender.user.birth_date)
        recipient_age = age_convert(t.recipient.user.birth_date)
        record = [
            sender_age,
            t.sender.user.gender,
            t.sender.user.address,
            t.sender.user.nationality,
            t.amount,
            recipient_age,
            t.recipient.user.gender,
            t.recipient.user.address,
            t.recipient.user.nationality,
            t.month,
            t.year
        ]
        testing.append(record)
        record_str = ','.join(map(str, record))
        all_transactions.append(record_str)

    # TESTING PURPOSES: Prints transaction history into file
    with open("staff/anonymise/data/og_transaction_history.data", "w") as file:
        for r in testing:
            file.write(", ".join(map(str, r)) + "\n")
    print("Transaction history data (not anonymised) printed to og_transaction_history.data")
    return all_transactions


def original_first_query():
    """
    Query: Average withdrawal amounts of Singaporean citizens for the past 5 years
    Use Case: High level view of average withdrawal amounts for researchers to gain insights on Singaporean 
    spending patterns

    The query is performed on all transaction data stored in the database and returns a datafile with the 
    results of the query.
    """
    # Get the table with age, gender, nationality, address (sender+recipient), transaction amount, month, year
    transactions = Transactions.objects.select_related('sender__user', 'recipient__user').filter(
        Q(sender__account=F('sender__account')) | Q(recipient__account=F('recipient__account'))
        ).select_related('sender__user__user', 'recipient__user__user')
    
    # For testing purposes, can remove after
    unfiltered_data = []
    for u in transactions:

        extract_year = ExtractYear(u.date)
        sender_age = age_convert(u.sender.user.birth_date)
        unfiltered = [
            sender_age,
            u.sender.user.gender,
            u.sender.user.address,
            u.sender.user.nationality,
            u.amount,
            extract_year
        ]
        unfiltered_data.append(unfiltered)

    # TESTING PURPOSES: Prints data into file unfiltered.data
    with open("staff/anonymise/data/unfiltered.data", "w") as file:
        for unfiltered in unfiltered_data:
            file.write(", ".join(map(str, unfiltered)) + "\n")
    print("I'm not sure what is in here: unfiltered.data")
    

    # Filter data based on the past five years and Singaporean citizens
    current_date = datetime.now()
    five_years_ago = current_date.replace(year=current_date.year - 4, month=1, day=1)
    citizen_yearly_transactions = transactions.filter(
        sender__user__nationality='Singaporean', date__gte=five_years_ago
        )
    group_transactions = citizen_yearly_transactions.annotate(
        year=ExtractYear('date')
    ).values(
        'sender__user__nationality', 'year'
    ).annotate(
        total_amount=Sum('amount'),
        num_transactions=Count('year')
    ).order_by(
        'year'
    )
 
    data = []
    all_transactions = list()
    for t in group_transactions:
        avg_amount = round((t['total_amount'] / t['num_transactions']), 2)
        year = t['year']
        record = [
            year,
            avg_amount
        ]
        data.append(record)
        record_str = ','.join(map(str, record))
        all_transactions.append(record_str)
    
    # TESTING PURPOSE: Prints queried unanonymised data to unanon_query.data
    with open("staff/anonymise/data/unanon_fquery.data", "w") as file:
        for record in data:
            file.write(", ".join(map(str, record)) + "\n")
    print("Unanonymised first query results printed to unanon_fquery.data")
    return all_transactions


def anonymised_first_query(data):
    """
    Query: Average withdrawal amounts of Singaporean citizens for the past 5 years
    Use Case: High level view of average withdrawal amounts for researchers to gain insights on Singaporean 
    spending patterns

    Takes in anonymised data as a dict and performs query on data. Outputs the result of query

    Constraints: 
    Will only process records where nationality == Singaporean, will not take any records with nationality
    suppressed
    """

    current_year = date.today().year
    past_five_years = current_year - 5

    # Filter the transaction data for Singaporeans in the past 5 years
    filtered_data = [
        d for d in data if(
            d['sender_nationality'] == 'Singaporean' and
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
    for year, data in yearly_data.items():
        total_amount = float(data['total_amount'])
        count = data['transaction_count']

        if count > 0:
            average_amount = round((total_amount / count), 2)
        else: 
            average_amount = 0
        
        yearly_data[year]['avg_amount'] = average_amount
   
    return yearly_data


def write_first_anon_query(query_data):
    """
        FOR TESTING: Writes query to file
    """
    with open("staff/anonymise/data/anonymised_fquery.data", 'w') as file:

        # Iterate through yearly_data and write each entry to the file
        for year, data in query_data.items():
            average_amount = data['avg_amount']
            file.write(f'{year}, {average_amount}\n')

    print('Data has been written to anonymised_fquery.data')


class QueryOptions(Enum):
    FIRST = "1"
    SECOND = "2"

class UserInputs():
    def __init__(self, k_value, query):
        self.k_value = k_value
        if query in [option.value for option in QueryOptions]:
            self.query = query
        else:
            raise ValueError("Invalid query option. Choose from 'F' or 'S'.")




def user_inputs(k, query):
    """
    Takes in user's input to perform anonymity using k-value and perform query on anonymised
    data. Performs query on both anonymised data and original data to calculate information loss
    """
    return {"anonymised": "data"} ## placeholder for testing of API
    new_input = UserInputs(k, query)
    transaction_history = retrieve_all_transactions()
    anonymised_data = anonymise(transaction_history, k)

    if new_input.query == "1":
        original_first_query()
        anon_query_data = anonymised_first_query(anonymised_data)
        write_first_anon_query(anon_query_data)
        

user_inputs(4, "1")







