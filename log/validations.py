def validate_query(json_dict):
    try:
        query = json_dict["query"]
    except KeyError:
        raise ValidationError("Field 'query' missing.")

    if query not in [option.value for option in QueryOptions]:
        raise ValidationError("Value in 'query' field is not a recognised option")
    
    return query