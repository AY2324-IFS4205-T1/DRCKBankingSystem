import csv
import io

import matplotlib.pyplot as plt
import numpy as np
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from anonymisation.models import Anonymisation, Statistics
from anonymisation.validations import (validate_k_is_set, validate_k_value,
                                       validate_query)
from anonymisation.wrapper import generate_k_anon, save_anon, set_k


class ViewAnonStatsSerializer(serializers.Serializer):

    def get_graph(self):
        self.get_statistics()
        self.plot_graph()
        return self.stream

    def get_statistics(self):
        self.k_values = list()
        self.info_losses = list()
        self.utilities_query1 = list()
        self.utilities_query2 = list()
        self.last_updated = timezone.now()

        for stat in Statistics.objects.all().order_by("k_value"):
            self.k_values.append(stat.k_value)
            self.info_losses.append(stat.info_loss)
            self.utilities_query1.append(stat.utility_query1)
            self.utilities_query2.append(stat.utility_query2)
            if stat.last_updated < self.last_updated:
                self.last_updated = stat.last_updated
        
        self.k_values = np.array(self.k_values)
        self.info_losses = np.array(self.info_losses)
        self.utilities_query1 = np.array(self.utilities_query1)
        self.utilities_query2 = np.array(self.utilities_query2)
        self.text = "Last updated: " + self.last_updated.__str__()
    
    def plot_graph(self):
        axis1 = plt.figure().add_axes((0.15,0.15,0.7,0.7))
        axis2 = axis1.twinx()

        axis1.plot(self.k_values, self.info_losses, "r", label="Information Loss")
        axis2.plot(self.k_values, self.utilities_query1, "b", label="Utility for Query 1")
        axis2.plot(self.k_values, self.utilities_query2, "g", label="Utility for Query 2")
        
        axis1.set_xlabel('k-value')
        axis1.set_ylabel('Information Loss')
        axis2.set_ylabel("Utility")
        lines, labels = axis1.get_legend_handles_labels()
        lines2, labels2 = axis2.get_legend_handles_labels()
        axis2.legend(lines + lines2, labels + labels2)
        plt.xticks(self.k_values)
        plt.title("Information Loss and Utility against k-value", fontweight="bold")
        plt.figtext(0.55, 0.01, self.text, horizontalalignment='left', fontsize=8)
        
        stream = io.BytesIO()
        plt.savefig(stream, format="png")
        stream.seek(0)
        self.stream = stream


class GetKValueSerializer(serializers.Serializer):
    def validate(self, attrs):
        self.statistic = validate_k_is_set()
        return super().validate(attrs)
    
    def get_k(self):
        return self.statistic.k_value


class SetKValueSerializer(serializers.Serializer):
    def __init__(self, json_dict, **kwargs):
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.k_value = validate_k_value(self.json_dict)
        try:
            self.anon_json = generate_k_anon(self.k_value)
        except Exception as error:
            raise ValidationError(error)
        return super().validate(attrs)
    
    def set_k(self):
        save_anon(self.anon_json)
        set_k(self.k_value)


class QueryAnonSerializer(serializers.Serializer):
    def __init__(self, json_dict, **kwargs):
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.statistic = validate_k_is_set()
        self.query = validate_query(self.json_dict)
        return super().validate(attrs)
    
    def get_query_results(self):
        results = dict()
        if self.query == "1":
            utility = self.statistic.utility_query1
            results["average of 2019 sums"] = self.statistic.first_average
            results["average of 2020 sums"] = self.statistic.second_average
            results["average of 2021 sums"] = self.statistic.third_average
            results["average of 2022 sums"] = self.statistic.fourth_average
            results["average of 2023 sums"] = self.statistic.fifth_average
        else:
            utility = self.statistic.utility_query2
            results["average savings balance"] = self.statistic.first_balance_average
            results["average credit card balance"] = self.statistic.second_balance_average
            results["average investment balance"] = self.statistic.third_balance_average
        
        response = dict()
        response["utility"] = utility
        response["results"] = results
        return response


class GetAnonDataSerializer(serializers.Serializer):
    def validate(self, attrs):
        self.statistic = validate_k_is_set()
        return super().validate(attrs)

    def get_anon_data(self, response):
        anon_fields = ["id", "age", "gender", "postal_code", "citizenship", "first_sum", "second_sum", "third_sum", "fourth_sum", "fifth_sum", "first_balance", "second_balance", "third_balance"]
        header = ["id", "age", "gender", "postal_code", "citizenship", "2019 sum", "2020 sum", "2021 sum", "2022 sum", "2023 sum", "savings balance", "credit card balance", "investment balance"]        
        writer = csv.writer(response)
        writer.writerow(header)
        for obj in Anonymisation.objects.all():
            writer.writerow([getattr(obj, field) for field in anon_fields])
        return response

