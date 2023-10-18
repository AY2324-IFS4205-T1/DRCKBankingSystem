from anonymisation.anonymise.overall import anonymise_wrapper, perform_query

from anonymisation.anonymise.utils.database import store_stats_database, store_anon_database
from anonymisation.models import Statistics

MINIMUM_K_VALUE = 3
MAXIMUM_K_VALUE = 5


def generate_statistics():
    Statistics.objects.all().delete()
    for i in range(MINIMUM_K_VALUE, MAXIMUM_K_VALUE+1):
        _, info_loss, anon_data = anonymise_wrapper(i)
        first_list, first_utility, _ = perform_query("1", anon_data)
        second_list, second_utility, _ = perform_query("2", anon_data)
        store_stats_database(i, info_loss, first_list, second_list, first_utility, second_utility)

def generate_k_anon(k_value):
    anon_json, info_loss, _ = anonymise_wrapper(k_value)
    return {"json_results": anon_json, "info_loss": info_loss}

def get_utility(query_number, anon_data):
    _, utility, result_json = perform_query(query_number, anon_data)
    return {"results": result_json, "utility": utility}

def save_anon(anon_data):
    store_anon_database(anon_data)

def set_k(k_value):
    stat_instance = Statistics()
    result = stat_instance.set_k_value_to_true(k_value)
    if result:
        return {f"K-Value {k_value} chosen"}
    else:
        return {"K-Value {k_value} does not exist"}
