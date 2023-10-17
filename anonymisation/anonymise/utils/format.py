import json

from datetime import datetime

from anonymisation.anonymise.utils.requirements import DecimalEncoder
    
class AnonymisedDataFormatterBase:
    def format_attributes(self, range):
        parts = range.split("~")
        output_string = " - ".join(parts)
        return output_string
    
    def anonymise_postal_code(self, input_string):
        parts = input_string.split(" - ")
        first_part = parts[0][:2] + "****"
        if len(parts) == 1:
            return first_part
        elif len(parts) == 2:
            second_part = parts[1][:2] + "****"
            result_string = f"{first_part} - {second_part}"
            return result_string
        return None
    
    def format_citizenship(self, input_string):
        formatted_string = input_string.replace("SingaporeanCitizen", "Singaporean Citizen")
        formatted_string = formatted_string.replace("SingaporeanPR", "Singapore PR")
        return formatted_string
    
    def format_anon_data(self, anon_data):
        formatted_data = []

        for d in anon_data:
            age_range = self.format_attributes(d['age'])
            gender_range = self.format_attributes(d['gender'])
            postal_code_range = self.format_attributes(d['postal_code'])
            anon_postal_code = self.anonymise_postal_code(postal_code_range)
            citizenship = self.format_attributes(d['citizenship'])
            spaced_citizenship = self.format_citizenship(citizenship)

            today_year = datetime.now().year
            
            record = {
                'age': age_range,
                'gender': gender_range,
                'postal_code': anon_postal_code,
                'citizenship': spaced_citizenship,
                f'{today_year-4}_sum': d['first_sum'],
                f'{today_year-3}_sum': d['second_sum'],
                f'{today_year-2}_sum': d['third_sum'],
                f'{today_year-1}_sum': d['fourth_sum'],
                f'{today_year}_sum': d['fifth_sum'],
                'savings_balance': d['first_balance'],
                'credit_card_balance': d['second_balance'],
                'investment_balance': d['third_balance']
            }
            formatted_data.append(record)

            # For TESTING PURPOSE: will form a dict with the formatted info and print
        json_data = json.dumps(formatted_data, indent=4, cls=DecimalEncoder)
        return json_data
