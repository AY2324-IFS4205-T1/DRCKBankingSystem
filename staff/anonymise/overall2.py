from django.db.models import F, Q, Sum, Count
from customer.models import Transactions
from django.db.models.functions import ExtractMonth, ExtractYear

import json
from enum import Enum
from datetime import datetime, date

from django.http import JsonResponse

from staff.anonymise.utils.anonymiser import anonymise
from staff.anonymise.utils.requirements import age_convert

from staff.anonymise.utils.format_anonymise import WithdrawalAnonymisedFormatter
from staff.anonymise.utils.query import AnonymisedFirstQuery, UnanonymisedFirstQuery


# First Query Parameters
TYPE_OF_CITIZEN = 'Singaporean Citizen'
NUM_YEARS = 10
TRANSACTION_TYPE = 'Withdrawal'

# TESTING PURPOSES: Get rid of this printing to json file
def write_to_json_file(json_data, file_name):
    file_path = "staff/anonymise/data/" + file_name

    with open(file_path, "w") as json_file:
        json_file.write(json_data)
    print(f"JSON data printed to {file_path}") 

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

class TransactionRetrieverBase:
    
    def __init__(self, type):
        self.type = type

    # REMOVE! FOR TESTING PURPOSE: Prints a string into a file
    def testing_print(self, testing_data, file_name):
        file_path = "staff/anonymise/data/" + file_name
        # TESTING PURPOSES: Prints transaction history into file
        with open(file_path, "w") as file:
            for r in testing_data:
                file.write(", ".join(map(str, r)) + "\n")
        print(f"{str(self.type)} data (not anonymised) printed to {file_name}")
    
    def retrieve(self):
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
            transaction_type=self.type).select_related('sender__user__user', 'recipient__user__user')
    
        transactions = query.annotate(
            month=ExtractMonth('date'),
            year=ExtractYear('date')
        )
        return transactions
    
    def format(self, transactions):
        # Method should be overridden for each subclass
        pass

class DepositRetriever(TransactionRetrieverBase):
    
    def format(self, transaction_data):
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
            record_str = ','.join(map(str, record))
            deposit_transactions.append(record_str)
            # REMOVE! FOR TESTING PURPOSE
            testing.append(record)

        return deposit_transactions, testing

class WithdrawalRetriever(TransactionRetrieverBase):   
    def format(self, transaction_data):
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
            record_str = ','.join(map(str, record))
            withdrawal_transactions.append(record_str)
            # REMOVE! FOR TESTING PURPOSE
            testing.append(record)

        return withdrawal_transactions, testing
    
class TransferRetriever(TransactionRetrieverBase):  
    def format(self, transaction_data):
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
            record_str = ','.join(map(str, record))
            transfer_transactions.append(record_str)
            # REMOVE! FOR TESTING PURPOSE
            testing.append(record)

        return transfer_transactions, testing
    
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

class TooShortException(Exception):
    pass

    
def user_inputs(k, query):
    new_input = UserInputs(k, query)
    if new_input.query == "1": # Average withdrawal amount of Singaporeans for the past 5 years
        withdrawal_retriever = WithdrawalRetriever('Withdrawal')
        withdrawal_history = withdrawal_retriever.retrieve()
        formatted_str_withdrawals, testing = withdrawal_retriever.format(withdrawal_history)

        # REMOVE! FOR TESTING PURPOSE
        file_name = f"unanon_{withdrawal_retriever.type.lower()}.data"
        withdrawal_retriever.testing_print(testing, file_name)
        
        
        # Handles null: returns an empty response
        if not withdrawal_history:
            return JsonResponse({})
        
        # Handles case when there is not enough data: raises error
        if len(withdrawal_history) < k:
            raise TooShortException("Not enough data for anonymisation.")
        
        # Anonymise the withdrawal data
        anon_withdrawal_data = anonymise(formatted_str_withdrawals, k, 'Withdrawal')
        anonymised_formatter = WithdrawalAnonymisedFormatter()

        # TODO: Need to know if this part need to return and how to return to view function that calls it
        anon_withdrawal_json = anonymised_formatter.format_anon_withdrawal_data(anon_withdrawal_data)
        write_to_json_file(anon_withdrawal_json, "anon_withdrawal.json")

        # Perform first query on anonymised data
        anon_first_query = AnonymisedFirstQuery(TYPE_OF_CITIZEN, NUM_YEARS, TRANSACTION_TYPE)
        testing, anon_first_json = anon_first_query.anonymised_first_query(anon_withdrawal_data)
        write_to_json_file(anon_first_json, "anon_query.json")

        # TESTING PURPOSES: Write the first query result to file
        write_first_anon_query(testing)

        # Perform first query on unanonymised data
        unanon_first_query = UnanonymisedFirstQuery(TYPE_OF_CITIZEN, NUM_YEARS, TRANSACTION_TYPE)
        _, unanon_first_json = unanon_first_query.unanonymised_first_query(withdrawal_history)
        write_to_json_file(unanon_first_json, "unanon_query.json")

        return {"anonymised": anon_first_json,
        "unanonymised": unanon_first_json} ## placeholder for testing of API



user_inputs(4, "1")