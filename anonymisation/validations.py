from rest_framework.serializers import ValidationError

from anonymisation.anonymise.overall import MAXIMUM_K_VALUE, QueryOptions


def validate_k_value(json_dict):
    try:
        k = int(json_dict["k_value"])
    except KeyError:
        raise ValidationError("Field 'k_value' missing.")
    except ValueError:
        raise ValidationError("K-value provided is not an integer")
    
    if k not in range(1, MAXIMUM_K_VALUE+1):
        raise ValidationError("K-value provided is not within the acceptable k-value range")
    
    return k

def validate_query(json_dict):
    try:
        query = json_dict["query"]
    except KeyError:
        raise ValidationError("Field 'query' missing.")

    if query not in [option.value for option in QueryOptions]:
        raise ValidationError("Value in 'query' field is not a recognised option")
    
    return query