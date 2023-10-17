import json

from rest_framework import serializers

from anonymisation.validations import validate_k_value, validate_query
from anonymisation.anonymise.overall import anonymise_wrapper, perform_query

class AnonymisationSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.k = validate_k_value(self.json_dict)
        return super().validate(attrs)

    def get_anonymised_data(self):
        try:
            data = anonymise_wrapper(self.k)
        except Exception as error:
            return {"error": error.__str__()}
        return {"data": data}

class QuerySerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.query = validate_query(self.json_dict)
        return super().validate(attrs)

    def get_query_result(self):
        try:
            data = perform_query(self.k_value)
        except Exception as error:
            return {"error": error.__str__()}
        return {"data": data}