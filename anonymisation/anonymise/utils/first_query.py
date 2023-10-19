import json
from datetime import datetime, date
import statistics

from anonymisation.models import Anonymisation
from django.db.models import Sum, Count, Avg

from anonymisation.anonymise.utils.requirements import DecimalEncoder


def calculate_utility(anon_list, unanon_list):
    absolute_differences = [abs(anon_avg - actual_avg) for anon_avg, actual_avg in zip(anon_list, unanon_list)]
    mae = sum(absolute_differences) / len(absolute_differences)
    average_average = statistics.mean(anon_list)

    if average_average != 0:
        utility = 1 - (mae / average_average)
    else:
        utility = 0
    print(round(utility * 100, 2))
    return round(utility * 100, 2)

def retrieve_data(citizenship):
    
    citizenship_status = citizenship.replace(" ","")
    query = Anonymisation.objects.filter(citizenship=citizenship_status)

    filtered_data = []
    for q in query:
        record = {
            'age': q.age,
            'gender': q.gender,
            'postal_code': q.postal_code,
            'citizenship': q.citizenship,
            'first_sum': float(q.first_sum),
            'second_sum': float(q.second_sum),
            'third_sum': float(q.third_sum),
            'fourth_sum': float(q.fourth_sum),
            'fifth_sum': float(q.fifth_sum),
            'first_balance': float(q.first_balance),
            'second_balance': float(q.second_balance),
            'third_balance': float(q.third_balance)
        }
        filtered_data.append(record)

    return filtered_data

class FirstQueryBase():
    def __init__(self, type_of_citizen, num_years, transaction_type):
        self.type_of_citizen = type_of_citizen
        self.num_years = num_years
        self.transaction_type = transaction_type


class AnonymisedFirstQuery(FirstQueryBase):
    def first_query(self, data):
        
        filtered_data = [
            d for d in data if(
                d['citizenship'] == self.type_of_citizen
            )
        ]
        
        sum_data, count_data = self.sum_of_transactions(filtered_data)
        all_averages = self.average_amount(sum_data, count_data)
        
        formatted_data = []
        results_list = list()
        
        current_year = date.today().year

        for i in range(self.num_years):
            year = current_year - (self.num_years - i) + 1
            record = {
                'average_amount': all_averages[i],
                'year': year
            }
            formatted_data.append(record)
            results_list.append(all_averages[i])
        json_data = json.dumps(formatted_data, indent=4, cls=DecimalEncoder)
        print(results_list)
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
        
        filtered_data = [
            d for d in data if(
                d['citizenship'] == self.type_of_citizen
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
            'account_type': i+1
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
