import requests
import json
import time

# Get a batch of number trivia fromi numbersapi.com.
# use number_trivia() to get trivia.

def number_trivia(start, end):
    check_error_trivia(start, end)
    original_start = start
    start = start
    result ={}
    while True:
        result.update(get_trivia(start, end))
        start += 100
        time.sleep(2)
        if start == end:
            result.update(get_trivia(start, end))
            break
        elif start > end:
            break
    for num in range(original_start, end+1):
        print(f"{str(num)} - {result[str(num)]}")
    return(result)

def get_trivia(start, end):
    API = "http://numbersapi.com/{}..{}".format(start, end)
    return(requests.get(API).json())

def check_error_trivia(start, end):
    if start > end:
        raise ValueError('Start should be smaller than or equal to end.')
    elif str(type(start)) != "<class 'int'>" or str(type(end)) != "<class 'int'>":
        raise ValueError('Can only take interger.')