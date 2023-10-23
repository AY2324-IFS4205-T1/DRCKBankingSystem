from rest_framework.serializers import ValidationError

from anonymisation.anonymise.overall import QueryOptions
from anonymisation.models import Statistics
from anonymisation.wrapper import MINIMUM_K_VALUE, MAXIMUM_K_VALUE


def validate_k_value(json_dict):
    try:
        k = int(json_dict["k_value"])
    except KeyError:
        raise ValidationError("Please input the k-value.")
    except ValueError:
        raise ValidationError("K-value provided must be an integer.")
    
    if k < MINIMUM_K_VALUE or k > MAXIMUM_K_VALUE:
        raise ValidationError("K-value provided is not within the acceptable k-value range.")
    return k


def validate_query(json_dict):
    try:
        query = json_dict["query"].strip()
    except KeyError:
        raise ValidationError("Please input the query.")

    if query not in [option.value for option in QueryOptions]:
        raise ValidationError("The query given is not a recognised option.")
    
    return query


def validate_k_is_set():
    try:
        statistic = Statistics.objects.get(set_k_value=True)
    except Statistics.DoesNotExist:
        raise ValidationError("K-value has not been set by DRCK Banking's Anonymisation Officer.")
    return statistic
