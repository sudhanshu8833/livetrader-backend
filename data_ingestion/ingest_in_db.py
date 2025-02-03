import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta
import time

DB_CONFIG = {
    "dbname": "live_trader_db",
    "user": "sudhanshu",
    "password": "a",
    "host": "localhost",  # Or your database host
    "port": 5433          # Default PostgreSQL port
}

# options_data = [
#     ("2025-01-01 09:15:00", "NIFTY", "2025-01-30", 18000, "CE", 5, 10, 3, 8, 1000),
#     ("2025-01-01 09:15:00", "NIFTY", "2025-01-30", 18500, "PE", 7, 12, 5, 10, 1200),
# ]

# index_data = [
#     ("2025-01-01 09:15:00", "NIFTY", 100, 110, 90, 105),
#     ("2025-01-01 09:15:00", "SENSEX", 40000, 41000, 39500, 40500)
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

def ingest_from_db(contracts_data = None, options_data = None):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        if contracts_data:
            execute_batch(cursor, INSERT_OPTIONS_CONTRACT, contracts_data)
            print(f"{len(contracts_data)} rows inserted into options_contract.")

        if options_data:
            execute_batch(cursor, INSERT_OPTIONS_DATA, options_data)
            print(f"{len(options_data)} rows inserted into options_data.")

        connection.commit()
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    except Exception as e:
        print(f"Error: {e}")
        return None

def ingest_data(index_data = None, options_data = None):
    try:
        # Connect to the database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Insert data into index_data table
        if index_data:
            execute_batch(cursor, INSERT_INDEX_DATA, index_data)
            print(f"{len(index_data)} rows inserted into index_data.")

        elif options_data:
            execute_batch(cursor, INSERT_OPTIONS, options_data)
            print(f"{len(options_data)} rows inserted into options.")

        # Commit the transaction
        connection.commit()
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    except Exception as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
    # finally:
    #     # Close the connection


# Run the ingestion function
# (INDEX)(YYYYMMDD)(STRIKE)(CE/PE)

if __name__ == "__main__":
    time1 = time.time()
    data = get_options_data()
    print(f"Time taken: {time.time() - time1}")
