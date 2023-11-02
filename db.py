import sqlite3
from sqlite3 import Error
from datetime import datetime

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_current_config(conn):
    current_utc = datetime.utcnow();
    cur = conn.cursor()
    # insert_data = f"INSERT INTO gh_configs values(1, 100, 100, 10, 10, '{current_utc}');"
    # cur.execute(insert_data)
    cur.execute("SELECT * FROM gh_configs ORDER BY timestamp DESC LIMIT 1;")

    rows = cur.fetchall()
    conn.commit()
    conn.close()

    return rows;


    # for row in rows:
    #     print(row)


def main():
    database = r"test.db"

    # create a database connection
    conn = create_connection(database)
    with conn:

        print("2. Query all tasks")
        select_current_config(conn)


if __name__ == "__main__":
    main()

#command to create db
#.open dbname

#command to create tabl
# CREATE TABLE your_table_name (
# gh INT,
# fahrenheitToggle INT,
# tempMax INT,
# humidityMax INT,
# tempMin INT,
# humidityMin INT,
# timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#  );
