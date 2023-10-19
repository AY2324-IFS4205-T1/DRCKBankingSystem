from rest_framework.serializers import ValidationError

from anonymisation.anonymise.overall import QueryOptions
from anonymisation.models import Statistics
from anonymisation.wrapper import MINIMUM_K_VALUE, MAXIMUM_K_VALUE


def validate_k_value(json_dict):
    try:
        k = int(json_dict["k_value"])
    except KeyError:
        raise ValidationError("Field 'k_value' missing.")
    except ValueError:
        raise ValidationError("K-value provided is not an integer.")
    
    if k < MINIMUM_K_VALUE or k > MAXIMUM_K_VALUE:
        raise ValidationError("K-value provided is not within the acceptable k-value range.")
    return k


def validate_query(json_dict):
    try:
        query = json_dict["query"]
    except KeyError:
        raise ValidationError("Field 'query' missing.")

    if query not in [option.value for option in QueryOptions]:
        raise ValidationError("Value in 'query' field is not a recognised option")
    
    return query


def validate_k_is_set():
    try:
        statistic = Statistics.objects.get(set_k_value=True)
    except Statistics.DoesNotExist:
        raise ValidationError("K-value has not been set by DRCK Banking's Anonymisation Officer.")
    return statistic