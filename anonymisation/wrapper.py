from anonymisation.anonymise.overall import anonymise_wrapper, perform_query

from anonymisation.anonymise.utils.database import store_stats_database, store_anon_database
from anonymisation.models import Statistics

MINIMUM_K_VALUE = 3
MAXIMUM_K_VALUE = 20


def generate_statistics():
    Statistics.objects.all().delete()
    anon_data = None
    for i in range(MINIMUM_K_VALUE, MAXIMUM_K_VALUE+1):
        info_loss, anon_data = anonymise_wrapper(i)
        # Handles case of empty database
        if anon_data is None:
            return
        save_statistics(anon_data, i, info_loss)
    return anon_data

def save_statistics(anon_data, k_value, info_loss):
    first_list, first_utility, _ = perform_query("1", anon_data)
    second_list, second_utility, _ = perform_query("2", anon_data)
    store_stats_database(k_value, info_loss, first_list, second_list, first_utility, second_utility)

def generate_k_anon(k_value):
    info_loss, anon_data = anonymise_wrapper(k_value)
    save_statistics(anon_data, k_value, info_loss)
    return anon_data

def get_utility(query_number, anon_data):
    _, utility, result_json = perform_query(query_number, anon_data)
    return {"results": result_json, "utility": utility}

def save_anon(anon_data):
    store_anon_database(anon_data)

def set_k(k_value):
    Statistics().set_k_value_to_true(k_value)