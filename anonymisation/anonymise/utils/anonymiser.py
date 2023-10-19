from anonymisation.anonymise.utils.mondrian import mondrian
from anonymisation.anonymise.utils.read_data import read_data

import json

# Read my test record
DATA_SELECT = 'a'
RELAX = False
k = 3

WITHDRAWAL_COLUMNS = ['sender_age', 'sender_gender', 'sender_postal_code', 'sender_citizenship',
                    'transaction_amount', 'month', 'year']

DEPOSIT_COLUMNS = ['recipient_age', 'recipient_gender', 'recipient_postal_code', 'recipient_citizenship',
                    'transaction_amount', 'month', 'year']

TRANSFER_COLUMNS = ['sender_age', 'sender_gender', 'sender_postal_code', 'sender_citizenship',
                    'recipient_age', 'recipient_gender', 'recipient_postal_code', 'recipient_citizenship',
                    'transaction_amount', 'month', 'year']

ANON_COLUMNS = ['age', 'gender', 'postal_code', 'citizenship', 
                'first_sum', 'second_sum', 'third_sum', 'fourth_sum', 'fifth_sum', 'first_balance',
                'second_balance', 'third_balance']

def convert_intuitive_order(intuitive_order, record, i, connect_str='~'):
    """
    Takes in the integer of categorical data and converts it back into its original form
    """
    vtemp = ''
    if connect_str in record[i]:
        temp = record[i].split(connect_str)
        raw_list = []
        for j in range(int(temp[0]), int(temp[1]) + 1):
            raw_list.append(intuitive_order[i][j])
        vtemp = connect_str.join(raw_list)
    else:
        vtemp = intuitive_order[i][int(record[i])]
    
    return vtemp

def covert_to_raw(result, intuitive_order, sa_num, qi_num):
    """
    Converts the results back into its intuitive order and appends SA back into list
    """

    covert_result = []
    qi_len = len(intuitive_order)
    for record in result:
        covert_record = []
        for i in range(qi_len):
            if len(intuitive_order[i]) > 0:
                temp = convert_intuitive_order(intuitive_order, record, i)
                covert_record.append(temp)
            else:
                covert_record.append(record[i])
        if sa_num > 0: # Checks if there are sensitive attributes
            temp = covert_record
            for i in range(sa_num):
                temp += [record[qi_num+i]]
            covert_result.append(temp)
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
        anonymised_data.append(user_data)
    with open("staff/anonymise/data/anonymised.json", "w") as json_file:
        json.dump(anonymised_data, json_file, indent=4)


def prepare_output(result):
    """
    Stores results into a dictionary for to prepare for query 
    """
    column_names = ANON_COLUMNS
    data_dict = []
    for row in result:
        row_dict = {}
        for i, col_name in enumerate(column_names):
            row_dict[col_name] = row[i]
        data_dict.append(row_dict)
    return data_dict


def get_result_one(data, intuitive_order, qi_num, sa_num, k=10):
    """
    Run Mondrian Algorithm one time, with k=10 as default. Returns anonymised data
    """
    result, eval_result = mondrian(data, k, RELAX, qi_num)

    # Convert numerical values back to categorical values if necessary
    if DATA_SELECT == 'a':
        result = covert_to_raw(result, intuitive_order, sa_num, qi_num)
    else:
        for r in result:
            r[-1] = ','.join(r[-1])

    return result, eval_result




def anonymise(transaction_data, k_value, _):
    """
    Main function for calling anonymising based on the different transaction types of data.
    Reads input value of k from user and anonymises transaction data that is parsed in.
    Returns data as dict.
    """
    # Read in Transaction History data
    # if transaction_type == 'Withdrawal' or transaction_type == 'Deposit':
    #     DATA, intuitive_order, qi_num, sa_num = read_withdrawal_deposit(transaction_data)
    # else:
    #     DATA, intuitive_order, qi_num, sa_num = read_transfer(transaction_data)
    DATA, intuitive_order, qi_num, sa_num = read_data(transaction_data)
    
    result, eval_result = get_result_one(DATA, intuitive_order, qi_num, sa_num, k_value)
    output = prepare_output(result)
    return output, eval_result