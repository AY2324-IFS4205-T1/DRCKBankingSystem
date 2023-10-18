from anonymisation.models import Anonymisation, Statistics
from django.db import connections

def reset_sequence():
    with connections['default'].cursor() as cursor:
        cursor.execute("ALTER SEQUENCE anonymisation.anon_id_seq RESTART;")

def store_anon_database(anon_data):
    Anonymisation.objects.all().delete()
    reset_sequence()
    for data in anon_data:
        anon_instance = Anonymisation(
            age=data['age'],
            gender=data['gender'],
            postal_code=data['postal_code'],
            citizenship=data['citizenship'],
            first_sum=data['first_sum'],
            second_sum=data['second_sum'],
            third_sum=data['third_sum'],
            fourth_sum=data['fourth_sum'],
            fifth_sum=data['fifth_sum'],
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
        third_balance_average=second_list[2]
    )
    anon_instance.save()