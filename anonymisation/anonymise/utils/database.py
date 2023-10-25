from decimal import Decimal

from django.db import connections
from django.utils import timezone

from anonymisation.models import Anonymisation, Statistics

MAX_VALUE = Decimal('9999999999999999999999999.99')

def clean_sum(check_sum):
    check_sum = Decimal(check_sum)
    if check_sum > MAX_VALUE:
        return MAX_VALUE
    else:
        return check_sum

def store_anon_database(anon_data):
    Anonymisation.objects.all().delete()
    if anon_data is None:
        return
    count = 0
    for data in anon_data:
        count += 1
        anon_instance = Anonymisation(
            id=count,
            age=data['age'],
            gender=data['gender'],
            postal_code=data['postal_code'],
            citizenship=data['citizenship'],
            first_sum=clean_sum(data['first_sum']),
            second_sum=clean_sum(data['second_sum']),
            third_sum=clean_sum(data['third_sum']),
            fourth_sum=clean_sum(data['fourth_sum']),
            fifth_sum=clean_sum(data['fifth_sum']),
            first_balance=data['first_balance'],
            second_balance=data['second_balance'],
            third_balance=data['third_balance']
        )
        anon_instance.save()

def store_stats_database(k_value, info_loss, first_list, second_list, first_utility, second_utility):
    anon_instance = Statistics(
        k_value=k_value,
        utility_query1=first_utility,
        utility_query2=second_utility,
        info_loss=info_loss,
        first_average=first_list[0],
        second_average=first_list[1],
        third_average=first_list[2],
        fourth_average=first_list[3],
        fifth_average=first_list[4],
        first_balance_average=second_list[0],
        second_balance_average=second_list[1],
        third_balance_average=second_list[2],
        last_updated=timezone.now()
    )
    anon_instance.save()