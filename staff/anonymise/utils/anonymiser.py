import copy
from staff.anonymise.utils.mondrian import mondrian
from staff.anonymise.utils.read_my_data import read_data as read_test
from staff.anonymise.utils.first_query_anon import read_first_query_data
import json

# Read my test record
DATA_SELECT = 'a'
RELAX = False
k = 3

def covert_to_raw(result, intuitive_order, SA_num, QI_num, connect_str='~'):
    """
    Converts the results back into its intuitive order and appends SA back into list
    """

    covert_result = []
    qi_len = len(intuitive_order)
    for record in result:
        covert_record = []
        for i in range(qi_len):
            if len(intuitive_order[i]) > 0:
                vtemp = ''
                if connect_str in record[i]:
                    temp = record[i].split(connect_str)
                    raw_list = []
                    for j in range(int(temp[0]), int(temp[1]) + 1):
                        raw_list.append(intuitive_order[i][j])
                    vtemp = connect_str.join(raw_list)
                else:
                    vtemp = intuitive_order[i][int(record[i])]
                covert_record.append(vtemp)
            else:
                covert_record.append(record[i])
        if isinstance(record[-1], str): # Checks if the last record is a string (not anonymised)
            temp = covert_record
            for i in range(SA_num):
                temp += [record[QI_num+i]]
            covert_result.append(temp)
        else:
            covert_result.append(covert_record + [connect_str.join(record[-1])])
    return covert_result


def write_first_anon(result):
    """
    Writes the anonymised data into json format file
    """
    anonymised_data = []
    # with open("staff/anonymise/data/anonymized.data", "w") as output:
    for r in result:
        user_data = {
            "age": r[0],
            "gender": r[1],
            "postalcode": r[2],
            "nationality": r[3],
            "month": r[4],
            "year": r[5],
            "amount": r[6]
        }
        # output.write(';'.join(r) + '\n')
        anonymised_data.append(user_data)
    with open("staff/anonymise/data/anonymised.json", "w") as json_file:
        json.dump(anonymised_data, json_file, indent=4)


def write_to_file(result):
    """
    TESTING PURPOSES: Write the anonymized transaction data to bf_query_anonymized.data 
    for testing
    """
    with open("staff/anonymise/data/bf_query_anonymised.data", "w") as output:
        for r in result:
            output.write(';'.join(r) + '\n')
    print("Anonymised data written to bf_query_anonymised.data")

def prepare_output(result):
    """
    Stores results into a dictionary for to prepare for query 
    """
    column_names = ['sender_age', 'sender_gender', 'sender_address', 'sender_nationality', 
                    'recipient_age', 'recipient_gender', 'recipient_address', 'recipient_nationality',
                    'transaction_amount', 'month', 'year']
    data_dict = []
    for row in result:
        row_dict = {}
        for i, col_name in enumerate(column_names):
            row_dict[col_name] = row[i]
        data_dict.append(row_dict)
    return data_dict


def get_result_one(data, intuitive_order, QI_num, SA_num, k=10):
    """
    Run Mondrian Algorithm one time, with k=10 as default. Returns anonymised data
    """
    result, eval_result = mondrian(data, k, RELAX, QI_num)

    # Convert numerical values back to categorical values if necessary
    if DATA_SELECT == 'a':
        result = covert_to_raw(result, intuitive_order, SA_num, QI_num)
    else:
        for r in result:
            r[-1] = ','.join(r[-1])
    
    # TESTING PURPOSES: Prints the result to file
    write_to_file(result)
    return result




def anonymise(transaction_data, k_value):
    """
    Reads input value of k from user and anonymises all transaction history data
    """
    MODEL = 's' # Choose strict mondrian
    DATA_SELECT = 'a'
    INPUT_K = k_value
    RELAX = False
    
    # Read in Transaction History data
    DATA, intuitive_order, QI_num, SA_num = read_test(transaction_data)

    result = get_result_one(DATA, intuitive_order, QI_num, SA_num, k_value)
    output = prepare_output(result)
    return output