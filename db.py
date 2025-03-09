import sqlite3
import score
import time

DB_PATH = "dbLedger.sqlite"

def insert_into_ledger(data_dict):
    """
    Inserts a record into the 'ledger' table based on the provided dictionary data.
    Excludes the 'id' field since it is an auto-incremented primary key.
    
    :param data_dict: Dictionary containing the transaction data.
    """
    # Define the columns (excluding 'id' since it auto-increments)
    columns = [
        "txn_hash", "from_address", "to_address", "value", "fee", "gas",
        "expiry", "comments", "status", "timestamp", "to_score", "from_score"
    ]

    from_score, to_score = score.score()
    data_dict["from_score"] = from_score
    data_dict["to_score"] = to_score
    data_dict["timestamp"] = str(int(time.time()))
    data_dict["status"] = "1"
    data_dict["comments"] = "1"
    data_dict["expiry"] = ""
    
    # Create placeholders for parameterized query
    placeholders = ", ".join(["?" for _ in columns])
    
    # Create SQL Insert Statement
    sql_query = f"INSERT INTO ledger ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Extract values from dictionary, defaulting to None if a key is missing
    values = tuple(data_dict.get(col, None) for col in columns)
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute the Insert query
        cursor.execute(sql_query, values)
        
        # Commit the transaction
        conn.commit()
        print("Record inserted successfully!")
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    
    finally:
        # Close the database connection
        conn.close()


def get_score(address):
    """
    Fetches the average score for a given address based on its occurrence in the ledger.
    
    :param address: The address for which to calculate the average score.
    :return: The average score or None if no transactions are found.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # SQL query to fetch relevant scores based on address match
        sql_query = """
            SELECT to_score FROM ledger WHERE to_address = ?
            UNION ALL
            SELECT from_score FROM ledger WHERE from_address = ?
        """
        
        # Execute query
        cursor.execute(sql_query, (address, address))
        scores = cursor.fetchall()  # Fetch all matching scores
        
        # Convert fetched values to a list of scores
        scores = [score[0] for score in scores if score[0] is not None]
        
        # Compute the average score
        avg_score = sum(scores) / len(scores) if scores else None
        
        return avg_score

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    
    finally:
        # Close the database connection
        conn.close()

data_dict = {
    "txn_hash": "abc123",
    "from_address": "0xSender",
    "to_address": "0xReceiver",
    "value": 100,
    "fee": 1,
    "gas": 21000,
}
# insert_into_ledger(data_dict)
# print(get_score("0xSender"))