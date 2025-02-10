import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta
import time

DB_CONFIG = {
    "dbname": "live_trader_db",
    "user": "sudhanshu",
    "password": "a",
    "host": "localhost", 
    "port": 5433
}

# options_data = [
#     ("2025-01-01 09:15:00", "NIFTY", "2025-01-30", 18000, "CE", 5, 10, 3, 8, 1000),
#     ("2025-01-01 09:15:00", "NIFTY", "2025-01-30", 18500, "PE", 7, 12, 5, 10, 1200),
# ]


# SQL statements for inserting data
INSERT_OPTIONS = """
    INSERT INTO options (
        time, symbol, expiration_date, strike_price, option_type, open, high, low, close, volume, oi, exchange
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;  
"""

INSERT_INDEX_DATA = """
    INSERT INTO index (
        time, symbol, open, high, low, close, volume, exchange
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;  
"""

INSERT_OPTIONS_CONTRACT = """
    INSERT INTO options_contract (
        contract, index, expiration_date, strike_price, option_type, exchange, token
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
"""

INSERT_OPTIONS_DATA = """
    INSERT INTO options_data (
        contract, time, open, high, low, close, volume, oi
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
"""

INSERT_INTO_HOLIDAYS = """
    INSERT INTO holidays (
        exchange, date
    ) VALUES (%s, %s)
    ON CONFLICT DO NOTHING;
"""

def get_options_data(starttime = None, endtime = None):
    query = """
        SELECT * FROM options where symbol = 'BANKNIFTY' limit 1000;
    """
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        print(f"Error: {e}")
        return None

def base_ingest_data(query, data):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        if data:
            execute_batch(cursor, query, data)
            print(f"{len(data)} rows inserted into some table.")

        connection.commit()
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    except Exception as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()


if __name__ == "__main__":
    time1 = time.time()
    data = get_options_data()
    print(data[0:1])
    print(f"Time taken: {time.time() - time1}")
