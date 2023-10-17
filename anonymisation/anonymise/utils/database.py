from anonymisation.models import Anonymisation
from django.db import connections

def reset_sequence():
    with connections['default'].cursor() as cursor:
        cursor.execute("ALTER SEQUENCE anonymisation.anon_id_seq RESTART;")

def save_to_database(anon_data):
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