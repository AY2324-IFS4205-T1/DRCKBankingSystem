from enum import Enum

from django.db.models import F, Q, Sum, Count
from customer.models import Transactions, Accounts
from django.db.models.functions import ExtractMonth, ExtractYear

from datetime import datetime

from django.http import JsonResponse

from anonymisation.anonymise.utils.anonymiser import anonymise
from anonymisation.anonymise.utils.requirements import age_convert
from anonymisation.anonymise.utils.first_query import calculate_utility

from anonymisation.anonymise.utils.format import AnonymisedDataFormatterBase
from anonymisation.anonymise.utils.first_query import AnonymisedFirstQuery, UnanonymisedFirstQuery, AnonymisedSecondQuery, UnanonymisedSecondQuery

# FIXED
NUM_YEARS1 = 5
TRANSACTION_TYPE1 = 'Withdrawal'

# First Query Parameters
TYPE_OF_CITIZEN1 = 'Singaporean Citizen'

# Second Query Parameters
TYPE_OF_CITIZEN2 = 'Singaporean Citizen'

class QueryOptions(Enum):
    FIRST = "1"
    SECOND = "2"
class TooShortException(Exception):
    pass

class TransactionRetrieverBase:
    
    def __init__(self, type, num_years):
        self.type = type
        self.num_years = num_years

    # REMOVE! FOR TESTING PURPOSE: Prints a string into a file
    def testing_print(self, testing_data, file_name):
        file_path = "anonymisation/anonymise/data/" + file_name
        # TESTING PURPOSES: Prints transaction history into file
        with open(file_path, "w") as file:
            for r in testing_data:
                file.write(testing_data + "\n")
        print(f"{str(self.type)} data (not anonymised) printed to {file_name}")
    
    def retrieve_transactions(self):
        """
        Retrieves the sum of withdrawal data for the past five years and the personal information of the customers
        """
        query = Transactions.objects.select_related('sender__user', 'recipient__user').filter(
            Q(sender__account=F('sender__account')) | Q(recipient__account=F('recipient__account')),
            transaction_type=self.type).select_related('sender__user__user', 'recipient__user__user')

        transactions = query.annotate(
            month=ExtractMonth('date'),
            year=ExtractYear('date')
        )
        current_date = datetime.now().year
        end_target_year = current_date
        start_target_year = end_target_year - self.num_years + 1
        # print(start_target_year)
        grouped_transactions = transactions.values(
            'sender__user__user', 'year', 'sender__user__gender', 'sender__user__postal_code',
            'sender__user__birth_date', 'sender__user__citizenship').filter(
                Q(year__gte=start_target_year) &
                Q(year__lte=end_target_year)
            ).annotate(
            total_amount=Sum('amount')
        )
        # for data in grouped_transactions:
        #     print(data)

        return grouped_transactions
    
    def retrieve_accounts(self):
        """
        Retrieves the balance of customer accounts, based on the THREE account types
        """
        query = Accounts.objects.select_related('user').values(
            'user__gender', 'user__postal_code', 'user__citizenship', 'user__birth_date',
            'type', 'user', 'balance'
        )

        return query

    def format(self, transactions):
        # Method should be overridden for each subclass
        pass

class WithdrawalRetriever(TransactionRetrieverBase):   
    def format(self, transaction_data=None, account_data=None):
        """
        Formats the data into a list, which will be anonymised

        """

        combined_records = self.include_withdrawals(transaction_data)

        combined_with_account = self.include_accounts(combined_records, account_data)

        formatted_data = [record for record in combined_with_account.values()]

        formatted_strings = [] 
        for record in formatted_data:
            record_str = [
                # str(record['sender_id']),
                str(record.get('sender_age', '')),
                str(record.get('gender', '')),
                str(record.get('postal_code', '')),
                str(record.get('citizenship', '')),
            ]

            years = range(datetime.now().year - self.num_years+1, datetime.now().year+1)
            total_amount = [str(record['total_amount'].get(year, 0)) for year in years]
            
            balances = record.get('balances', {})
            
            account_balances = [balances.get(str(account_type), 0) for account_type in range(1, 4)]

            record_str.extend(total_amount)
            record_str.extend(account_balances)

            formatted_strings.append(','.join(map(str, record_str)))

        return formatted_strings
    
    def include_withdrawals(self, transaction_data):
        """
        Formats the sum of withdrawals for the past 5 years and inserts it into a dictionary 
        """
        combined_records = {}
       
        for t in transaction_data:
            sender_id = str(t['sender__user__user'])
            year = t['year']
            total_amount = str(t['total_amount'])
            gender = t['sender__user__gender']
            postal_code = t['sender__user__postal_code']
            citizenship = t['sender__user__citizenship']
            sender_age = str(age_convert(t['sender__user__birth_date']))
            
            key = (sender_id, sender_age, gender, postal_code, citizenship)
            
            if key not in combined_records:
                combined_records[key] = {
                    'sender_id': str(sender_id),
                    'sender_age': str(sender_age),
                    'gender': str(gender),
                    'postal_code': str(postal_code),
                    'citizenship': str(citizenship), 
                    'total_amount': {year: str(total_amount)},
                }
                
            else:
                combined_records[key].setdefault('total_amount', {})[year] = str(total_amount)
                combined_records[key].setdefault('balances', {})

        return combined_records
    
    def include_accounts(self, transaction_dict, account_data):
        """
        Formats the balance of each account type and returns it into a dictionary, combined with sum of withdrawals 
        """
        for a in account_data:
            user_id = str(a['user'])
            gender = str(a['user__gender'])
            postal_code = str(a['user__postal_code'])
            citizenship = str(a['user__citizenship'])
            account_type = str(a['type'])
            balance = str(a['balance'])
            age = str(age_convert(a['user__birth_date']))

            key = (user_id, age, gender, postal_code, citizenship)

            if key not in transaction_dict:
                transaction_dict[key] = {
                    'sender_id': str(user_id),
                    'sender_age': str(age),
                    'gender': str(gender),
                    'postal_code': str(postal_code),
                    'citizenship': str(citizenship),
                    'balances': {account_type: str(balance)},
                    'total_amount': {}
                }
            else:
                transaction_dict[key].setdefault('balances', {})[account_type] = str(balance)

        return transaction_dict

# TESTING PURPOSES: Get rid of this printing to json file
def write_to_json_file(json_data, file_name):
    file_path = "anonymisation/anonymise/data/" + file_name

    with open(file_path, "w") as json_file:
        json_file.write(json_data)
    print(f"JSON data printed to {file_path}") 


def first_query_wrapper(anon_data, raw_data):
    anon_first_query = AnonymisedFirstQuery(TYPE_OF_CITIZEN1, NUM_YEARS1, TRANSACTION_TYPE1)
    anon_first_json, anon_list = anon_first_query.first_query(anon_data)
    
    write_to_json_file(anon_first_json, "anon_first.json")

    unanon_first_query = UnanonymisedFirstQuery(TYPE_OF_CITIZEN1, NUM_YEARS1, TRANSACTION_TYPE1)
    unanon_first_json, unanon_list = unanon_first_query.first_query(raw_data)
    
    write_to_json_file(unanon_first_json, "unanon_first.json")

    utility = calculate_utility(anon_list, unanon_list)
    return anon_list, utility, anon_first_json


def second_query_wrapper(anon_data, raw_data):
    anon_second_query = AnonymisedSecondQuery(TYPE_OF_CITIZEN2)
    anon_second_json, anon_list = anon_second_query.second_query(anon_data)
    
    write_to_json_file(anon_second_json, "anon_second.json")

    unanon_second_query = UnanonymisedSecondQuery(TYPE_OF_CITIZEN2)
    unanon_second_json, unanon_list = unanon_second_query.second_query(raw_data)
    
    write_to_json_file(unanon_second_json, "unanon_second.json")

    utility = calculate_utility(anon_list, unanon_list)
    return anon_list, utility, anon_second_json


def perform_query(query_option, anon_data):
    
    # For unanonymised, have to do initial retrieval and then do the processing
    retriever = WithdrawalRetriever('Withdrawal', NUM_YEARS1)
    
    if anon_data is None:
        return None, 0, None
    if query_option == "1":
        raw_data = retriever.retrieve_transactions()
        anon_list, utility, result_json = first_query_wrapper(anon_data, raw_data)
    elif query_option == "2":
        raw_data = retriever.retrieve_accounts()
        anon_list, utility, result_json = second_query_wrapper(anon_data, raw_data)
    else:
        return None, 0, None
    return anon_list, utility, result_json

    
# Main Function  
def anonymise_wrapper(k_value):
    retriever = WithdrawalRetriever('Withdrawal', NUM_YEARS1)
    
    transaction_info = retriever.retrieve_transactions()
    account_info = retriever.retrieve_accounts()
    
    formatted_str_withdrawals = retriever.format(transaction_info, account_info)

    if not formatted_str_withdrawals:
        return None, 0, None
    
    if len(formatted_str_withdrawals) < k_value:
        raise TooShortException("Not enough data for anonymisation.")
    
    anon_data, eval_result = anonymise(formatted_str_withdrawals, k_value, retriever.type)
    anonymised_formatter = AnonymisedDataFormatterBase()
    
    anon_json = anonymised_formatter.format_anon_data(anon_data)
    
    
    # TESTING PURPOSE: REMOVE
    write_to_json_file(anon_json, f"anon_{retriever.type.lower()}.json")
    
    info_loss = round(eval_result[0], 2)
    # rtime = eval[1]
    # print("Running time %0.2f" % rtime + " seconds")
    
    # print(eval_result[0])

    return anon_json, info_loss, anon_data

# Main Function
# k_value = 5
# _, _, anon_data = anonymise_wrapper(k_value)
# perform_query("1", anon_data)
