import sqlite3
from sqlite3 import Error
import json

def create_connection(db_file):
    conn = None
    try:
        print("succeed")
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

# update existing configs based on gather info from settings page
# requires a complete config file even if only some values are changed
def update_existing_configs(config):
    # will need changed to the location of the DB on the linux machine
    conn = create_connection("./gh_confs.db")
    cur = conn.cursor()

    try:
        # list of configs generated from the passed in config
        configs = [config["1"], config["2"], config["3"], config["4"], config["5"], config["6"]]

        cur.execute("SELECT * from gh_configs;")
        entries = cur.fetchall()
        # print(entries)

        
        gh = 1
        for c in configs: # loop through the configs and use the values of each to update the existing ones in the db
            if len(entries) == 0:
                print("We are inserting")
                insert = f"INSERT INTO gh_configs (gh, tempMax, tempMin, humidityMax, humidityMin) \
                VALUES ('{str(gh)}', {c['tempMax']}, {c['tempMin']}, {c['humidityMax']}, {c['humidityMin']});"
                cur.execute(insert)
            else:
                print("We are updating")
                command = f"UPDATE gh_configs SET tempMax = {c['tempMax']}, tempMin = {c['tempMin']}, \
                    humidityMax = {c['humidityMax']}, humidityMin = {c['humidityMin']} \
                        WHERE gh = {str(gh)};"
                cur.execute(command)
            gh = gh + 1; # keep track of the greenhouse that we are on (id)
        conn.commit()

        print("Update / Insert Complete")
        
    except sqlite3.Error as e:
        print(e)

    finally:
        conn.close()

def set_temp_unit(is_celsius: bool):
    conn = create_connection("./gh_confs.db")
    cur = conn.cursor()

    cur.execute("select * from temp_unit;")
    value = cur.fetchall()

    if len(value) == 0:
        cur.execute(f"INSERT INTO temp_unit (is_celsius) VALUES ({is_celsius});")
    else:
        cur.execute(f"UPDATE temp_unit SET is_celsius = {is_celsius};")

    conn.commit()
    conn.close()


def get_temp_unit():
    conn = create_connection("./gh_confs.db")
    cur = conn.cursor()

    cur.execute("SELECT * from temp_unit;")
    temp_bool = cur.fetchall()

    to_send = {"is_celsius" : None }
    if (len(temp_bool) > 0):
        to_send["is_celsius"] = bool(temp_bool[0][0])

    print(to_send)
    conn.close()
    return to_send


# grabs current config from db and stores it in json object
def select_current_configs():
    # will need changed to the location of the DB on the linux machine
    conn = create_connection("./gh_confs.db")

    cur = conn.cursor()

    cur.execute("SELECT * FROM gh_configs;")

    rows = cur.fetchall()

    to_send = {
        "1" : {
        "tempMax": 0,
        "tempMin": 0,
        "humidityMax": 0,
        "humidityMin": 0,
        },
        "2" : {
        "tempMax": 0,
        "tempMin": 0,
        "humidityMax": 0,
        "humidityMin": 0,
        },
        "3" : {
        "tempMax": 0,
        "tempMin": 0,
        "humidityMax": 0,
        "humidityMin": 0,
        },
        "4" : {
        "tempMax": 0,
        "tempMin": 0,
        "humidityMax": 0,
        "humidityMin": 0,
        },
        "5" : {
        "tempMax": 0,
        "tempMin": 0,
        "humidityMax": 0,
        "humidityMin": 0,
        },
        "6" : {
        "tempMax": 0,
        "tempMin": 0,
        "humidityMax": 0,
        "humidityMin": 0,
        }
    }

    # loop through rows of returned info and store them in there correct spot in the json object
    current_gh = 0
    
    # row format (id: 1, tMax: 50, hMax: 50, tMin30, hmin30)
    for r in rows:
        current_gh = current_gh + 1
        to_send[str(current_gh)]["tempMax"] = r[1]
        to_send[str(current_gh)]["tempMin"] = r[3]
        to_send[str(current_gh)]["humidityMax"] = r[2]
        to_send[str(current_gh)]["humidityMin"] = r[4]

    conn.close()
    return json.dumps(to_send)
