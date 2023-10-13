import json
from datetime import datetime, date
from decimal import Decimal
import math
import statistics

from django.db.models import F, Q, Sum, Count
from customer.models import Transactions
from django.db.models.functions import ExtractMonth, ExtractYear

from staff.anonymise.utils.requirements import DecimalEncoder, age_convert
from django.core import serializers

def calculate_utility(anon_list, unanon_list):
    absolute_differences = [abs(anon_avg - actual_avg) for anon_avg, actual_avg in zip(anon_list, unanon_list)]
    mae = sum(absolute_differences) / len(absolute_differences)
    average_average = statistics.mean(anon_list)
    print("MAE", mae)
    if average_average != 0:
        utility = 1 - (mae / average_average)
    else:
        utility = 0
    print(utility)
    return utility

class FirstQueryBase():
    def __init__(self, type_of_citizen, num_years, transaction_type):
        self.type_of_citizen = type_of_citizen
        self.num_years = num_years
        self.transaction_type = transaction_type


class AnonymisedFirstQuery(FirstQueryBase):
    def first_query(self, data):
        current_year = date.today().year


        citizenship_status = self.type_of_citizen
        citizenship_status = citizenship_status.replace(" ","")

        # Filter the transaction data for Singaporeans in the past 5 years
        filtered_data = [
            d for d in data if(
                d['citizenship'] == citizenship_status
            )
        ]
        sum_data, count_data = self.sum_of_transactions(filtered_data)
        all_averages = self.average_amount(sum_data, count_data)
        
        formatted_data = []
        results_list = list()
        
        for i in range(self.num_years):
            year = current_year - (self.num_years - i) + 1
            record = {
                'average_amount': all_averages[i],
                'year': year
            }
            formatted_data.append(record)
            results_list.append(all_averages[i])
        json_data = json.dumps(formatted_data, indent=4, cls=DecimalEncoder)
        
        return json_data, results_list
    
    def sum_of_transactions(self, data):

        sum_withdrawals = [0,0,0,0,0]
        count = [0,0,0,0,0]
        withdrawal_key = ['first_sum', 'second_sum', 'third_sum', 'fourth_sum', 'fifth_sum']

        current_year = datetime.now().year

        # Sum of all transactions and total number of transactions
        for t in data:
            for i in range(5):
                year = current_year - (self.num_years - i) + 1
                key = withdrawal_key[i]
                if key in t and float(t[key]) != 0:
                    sum_withdrawals[i] += float(t[key])
                    count[i] += 1
        
        return sum_withdrawals, count
    
    def average_amount(self, year_total, num_customers):
        average_list = list()    
        # Calculate the average amount of transactions
        for i in range(5):
            if year_total[i] != 0:
                average = year_total[i] / num_customers[i]
                average_list.append(average)
            else:
                average_list.append(0)
        return average_list
    
class UnanonymisedFirstQuery(FirstQueryBase):
    def first_query(self, raw_data):
        query = raw_data.filter(
            sender__user__citizenship=self.type_of_citizen
        ).order_by('year')

        
        current_year = datetime.now().year

        sum_of_all = [0,0,0,0,0]
        num_people = [0,0,0,0,0]

        for q in query:
            year = int(q['year'])
            index = year - current_year + 4
            amount = float(q['total_amount'])
            sum_of_all[index] += amount
            num_people[index] += 1

        all_averages = self.average_amount(sum_of_all, num_people)

        formatted_data = []
        results_list = list()

        for i in range(self.num_years):
            year = current_year - (self.num_years - i) + 1
            record = {
            'average_amount': all_averages[i],
            'year': year
            }
            formatted_data.append(record)
            results_list.append(all_averages[i])
        json_data = json.dumps(formatted_data, indent=4, cls=DecimalEncoder)
        return json_data, results_list
    
    def average_amount(self, total, num_people):    

        averages = list()

        for i in range(5):
            if total[i] != 0:
                avg = total[i] / num_people[i]
                averages.append(avg)
            else:
                averages.append(0)
        return averages

class SecondQueryBase():
    def __init__(self, type_of_citizen):
        self.type_of_citizen = type_of_citizen

class AnonymisedSecondQuery(SecondQueryBase):
    def second_query(self, data):
        citizenship_status = self.type_of_citizen
        citizenship_status = citizenship_status.replace(" ","")
        filtered_data = [
            d for d in data if(
                d['citizenship'] == citizenship_status
            )
        ]
        sum_data, count_data = self.sum_of_transactions(filtered_data)
        all_averages = self.average_amount(sum_data, count_data)

        formatted_data = []
        results_list = list()
        
        for i in range(3):
            account_type = i + 1
            record = {
                'average_amount': all_averages[i],
                'account_type': account_type
            }
            formatted_data.append(record)
            results_list.append(all_averages[i])
        json_data = json.dumps(formatted_data, indent=4, cls=DecimalEncoder)
        
        return json_data, results_list

    def sum_of_transactions(self, data):
    
        sum_balance = [0,0,0]
        count = [0,0,0]
        withdrawal_key = ['first_balance', 'second_balance', 'third_balance']

        current_year = datetime.now().year

        # Sum of all transactions and total number of transactions
        for t in data:
            for i in range(3):
                key = withdrawal_key[i]
                if key in t and float(t[key]) != 0:
                    sum_balance[i] += float(t[key])
                    count[i] += 1
        
        return sum_balance, count
    
    def average_amount(self, year_total, num_customers):
        average_list = list()    
        # Calculate the average amount of transactions
        for i in range(3):
            if year_total[i] != 0:
                average = year_total[i] / num_customers[i]
                average_list.append(average)
            else:
                average_list.append(0)
        return average_list

class UnanonymisedSecondQuery(SecondQueryBase):
    def second_query(self, raw_data):
        query = raw_data.filter(
            user__citizenship=self.type_of_citizen
        ).order_by('type')

        sum_of_all = [0,0,0]
        num_people = [0,0,0]

        for q in query:
            index = int(q['type'])
            amount = float(q['balance'])
            sum_of_all[index-1] += amount
            num_people[index-1] += 1
        
        all_averages = self.average_amount(sum_of_all, num_people)

        formatted_data = []
        results_list = list()

        for i in range(3):
            record = {
            'average_amount': all_averages[i],
            'account_type': i
            }
            formatted_data.append(record)
            results_list.append(all_averages[i])
        
        json_data = json.dumps(formatted_data, indent=4, cls=DecimalEncoder)
        return json_data, results_list
    
    def average_amount(self, total, num_people):    

        averages = list()

        for i in range(3):
            if total[i] != 0:
                avg = total[i] / num_people[i]
                averages.append(avg)
            else:
                averages.append(0)
        return averages
