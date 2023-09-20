"""
Read transaction history data set
"""

# !/usr/bin/env python
# coding=utf-8



ATT_NAME = ['sender_age', 'sender_gender', 'sender_address', 'sender_nationality', 
            'amount', 'recipient_age', 'recipient_gender', 'recipient_address', 'recipient_nationality',
            'month', 'year']
QI_INDEX = [0, 1, 2, 3, 5, 6, 7, 8]
IS_CAT = [False, True, False, True, False, True, False, True]
SA_INDEX = [4, 9, 10]
__DEBUG = False


def read_data(transaction_data):
    """

    Reads data and processes categorical data into integer values for anonymisation
   
    Parameters
    ----------
    transaction_data : str
        The unanonymised data set which contains transaction history of all customers
    
    Returns
    -------
    list
        list of all the processed data 
    intuitive_order
        list of all categorical data headers
    QI_num
        int value of length of quasi-identifier list
    SA_num
        int value of length of sensitive attributes list

    """
    QI_num = len(QI_INDEX)
    SA_num = len(SA_INDEX)
    data = []
    # order categorical attributes in intuitive order
    # here, we use the appear number
    intuitive_dict = []
    intuitive_order = []
    intuitive_number = []
    for i in range(QI_num):
        intuitive_dict.append(dict())
        intuitive_number.append(0)
        intuitive_order.append(list())
    
    for line in transaction_data:
        line = line.strip()
        # remove empty and incomplete lines
        # only 30162 records will be kept

        if len(line) == 0 or '?' in line:
            continue
        
        # remove double spaces
        line = line.replace(' ', '')
        temp = line.split(',')
        ltemp = []
        for i in range(QI_num):
            index = QI_INDEX[i]
            if IS_CAT[i]:
                try:
                    ltemp.append(intuitive_dict[i][temp[index]])
                except KeyError:
                    intuitive_dict[i][temp[index]] = intuitive_number[i]
                    ltemp.append(intuitive_number[i])
                    intuitive_number[i] += 1
                    intuitive_order[i].append(temp[index])
            else:
                ltemp.append(int(temp[index]))
       
        # Append SA after processing of QI
        for l in range(SA_num):
            left = SA_INDEX[l]
            ltemp.append(temp[left])
        data.append(ltemp)
    return data, intuitive_order, QI_num, SA_num
