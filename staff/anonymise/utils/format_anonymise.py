import json
from staff.anonymise.utils.requirements import DecimalEncoder
    
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
    
class WithdrawalAnonymisedFormatter(AnonymisedDataFormatterBase):
    def format_anon_withdrawal_data(self, anon_withdrawal):
        formatted_data = []
    
        for withdrawal in anon_withdrawal:
            age_range = self.format_attributes(withdrawal['sender_age'])
            gender_range = self.format_attributes(withdrawal['sender_gender'])
            postal_code_range = self.format_attributes(withdrawal['sender_postal_code'])
            anon_postal_code = self.anonymise_postal_code(postal_code_range)
            citizenship = self.format_attributes(withdrawal['sender_citizenship'])
            spaced_citizenship = self.format_citizenship(citizenship)
            
            record = {
                'sender_age': age_range,
                'sender_gender': gender_range,
                'sender_postal_code': anon_postal_code,
                'sender_citizenship': spaced_citizenship,
                'transaction_amount': withdrawal['transaction_amount'],
                'month': withdrawal['month'],
                'year': withdrawal['year']
            }
            formatted_data.append(record)

            # For TESTING PURPOSE: will form a dict with the formatted info and print
        json_data = json.dumps(formatted_data, indent=4, cls=DecimalEncoder)
        return json_data
