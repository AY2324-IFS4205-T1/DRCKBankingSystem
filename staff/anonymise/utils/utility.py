# !/usr/bin/env python
# coding:utf-8
"""
public functions
"""

from datetime import datetime
import time

def cmp(x, y):
    if x > y:
        return 1
    elif x==y:
        return 0
    else:
        return -1


def cmp_str(element1, element2):
    """
    compare number in str format correctley
    """
    try:
        return cmp(int(element1), int(element2))
    except ValueError:
        return cmp(element1, element2)

def cmp_value(element1, element2):
    if isinstance(element1, str):
        return cmp_str(element1, element2)
    else:
        return cmp(element1, element2)


def value(x):
    '''Return the numeric type that supports addition and subtraction'''
    if isinstance(x, (int, float)):
        return float(x)
    elif isinstance(x, datetime):
        return time.mktime(x.timetuple())
    else:
        try:
            return float(x)
        except Exception:
            return x


def merge_qi_value(x_left, x_right, connect_str='~'):
    '''Connect the interval boundary value as a generalized interval and return the result as a string
    return:
        result:string
    '''
    if isinstance(x_left, (int, float)):
        if x_left == x_right:
            result = '%d' % (x_left)
        else:
            result = '%d%s%d' % (x_left, connect_str, x_right)
    elif isinstance(x_left, str):
        if x_left == x_right:
            result = x_left
        else:
            result = x_left + connect_str + x_right
    elif isinstance(x_left, datetime):
        # Generalize the datetime type value
        begin_date = x_left.strftime("%Y-%m-%d %H:%M:%S")
        end_date = x_right.strftime("%Y-%m-%d %H:%M:%S")
        result = begin_date + connect_str + end_date
    return result


