
'''
1. no spaces in symbol
2. symbol should be in uppercase
3. no '.' in symbol
'''
from ingest_in_db import ingest_data
from helper import get_all_file_names, preprocess_date
import re
from datetime import datetime
import time

directory = "./options_data"
year = 24
months = [
    'january',
    'february', 
    'march', 
    'april', 
    'may', 
    'june', 
    'july', 
    'august',
    'september', 
    'october', 
    'november', 
    'december'
]

def process_option_symbol(contract):
    try:
        pattern = re.compile(r'([A-Za-z-&]+)(\d{6})(\d+\.?\d*)([A-Z]+)')
        match = pattern.match(contract)
        if match:
            symbol, yymmdd, strike, option_type = match.groups()
            return {
                'symbol': symbol,
                'expiry': datetime.strptime(yymmdd, '%y%m%d').date(),
                'strike': float(strike),
                'option_type': option_type
            }
        else:
            raise ValueError("Contract format is incorrect")
    except Exception as e:
        print(contract)
        raise e

def file_handeling(file, path):
    resultant_data = []
    if not ('NIFTY' in file or 'BANKNIFTY' in file):
        return resultant_data

    try:
        with open(path + '/' + file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                result_data = []
                data = line.split(',')
                date = preprocess_date(f'{data[1]} {data[2]}')
                result_data.append(date)
                symbol_object = process_option_symbol(data[0])
                data[-1].replace('\n', '')
                result_data = result_data + [symbol_object['symbol'], symbol_object['expiry'], symbol_object['strike'], symbol_object['option_type']]
                result_data = result_data + [float(data[3]), float(data[4]), float(data[5]), float(data[6]), float(data[7]), float(data[8])]
                result_data.append('NSE')
                resultant_data.append(tuple(result_data))
        return resultant_data   
    except Exception as e:
        print(e)
        return []

def start_ingestion():

    for month in months:
        time_before = time.time()
        path = directory + '/' + month
        csv_files = get_all_file_names(path)
        data_to_ingest = []
        for file in csv_files:
            data_to_ingest += file_handeling(file, path)
        print(f"Time taken for calculation of {month} is {time.time() - time_before}")
        temp_time = time.time()
        ingest_data(None, data_to_ingest)
        print(f"Time taken for ingestion of {month} is {time.time() - temp_time}")

if __name__ == '__main__':
    start_ingestion()