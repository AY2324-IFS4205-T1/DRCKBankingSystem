import json
from datetime import datetime, date

from django.db.models import F, Q, Sum, Count
from customer.models import Transactions
from django.db.models.functions import ExtractMonth, ExtractYear

from staff.anonymise.utils.requirements import DecimalEncoder, age_convert

class FirstQueryBase():
    def __init__(self, type_of_citizen, num_years, transaction_type):
        self.type_of_citizen = type_of_citizen
        self.num_years = num_years
        self.transaction_type = transaction_type

class AnonymisedFirstQuery(FirstQueryBase):
    """
    Query: Average withdrawal amounts of Singaporean citizens for the past 10 years
    Use Case: High level view of average withdrawal amounts for researchers to gain insights on Singaporean 
    spending patterns

    Takes in anonymised data as a dict and performs query on data. Returns the query as a dict for displaying

    Constraints: 
    Will only process records where citizenship == Singaporean Citizen, will not take any records with nationality
    suppressed

    TESTING PURPOSES: Returns yearly_data as dict so that can print
    """
    

    def anonymised_first_query(self, data):
        current_year = date.today().year
        past_five_years = current_year - self.num_years
        citizenship_status = self.type_of_citizen
        citizenship_status = citizenship_status.replace(" ","")

        # Filter the transaction data for Singaporeans in the past 5 years
        filtered_data = [
            d for d in data if(
                d['sender_citizenship'] == citizenship_status and
                int(d['year']) > past_five_years
            )
        ]
        sum_data = self.sum_of_transactions(filtered_data)
        testing, query_result = self.average_amount(sum_data)
        return testing, query_result
    
    def sum_of_transactions(self, data):
        yearly_data = {}

        # Sum of all transactions and total number of transactions
        for t in data:
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
        
        return yearly_data
    
    def average_amount(self, yearly_data):    
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

        # TESTING PURPOSES: Returns dict yearly_data to send to function for printing
        return yearly_data, json_data

class UnanonymisedFirstQuery(FirstQueryBase):

    def unanonymised_first_query(self, withdrawal_history):
        """
        The query is performed on all unanonymised transaction data stored in the database and returns a string of data.

        TESTING PURPOSE: 
            - unfiltered.data: Unanonymised data before query is performed on it
            - unanon_query.data: Unanonymised data after query is performed on it
        """
        
        # FOR TESTING PURPOSE: REMOVE THIS PART + FUNCTION
        self.testing_unfiltered_data(withdrawal_history)

        # Filter data based on the past five years and Singaporean citizens
        current_date = datetime.now()
        five_years_ago = current_date.replace(year=current_date.year - self.num_years + 1, month=1, day=1, hour=0, minute=0, second=0)
        formatted_datetime = five_years_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        citizen_yearly_transactions = withdrawal_history.filter(
            sender__user__citizenship=self.type_of_citizen, date__gte=formatted_datetime
            )
        group_transactions = citizen_yearly_transactions.values(
            'sender__user__citizenship', 'year'
        ).annotate(
            total_amount=Sum('amount'),
            num_transactions=Count('year')
        ).order_by(
            'year'
        )
        testing, json_output = self.average_amount(group_transactions)
        return testing, json_output
        
    def average_amount(self, total_transactions):    
        data = []
        data_json = []
        all_transactions = list()
        for t in total_transactions:
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
    
    # Remove! FOR TESTING PURPOSE ONLY
    def testing_unfiltered_data(self, transactions):
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