import sqlite3
from sqlite3 import Error
import json
from datetime import datetime

def create_connection(db_file):
    conn = None
    try:
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


def set_alert_value(is_triggered: bool):
    print('\nSETTING ALERT TO', is_triggered, '\n')
    conn = create_connection("./gh_confs.db")
    cur = conn.cursor()

    cur.execute("select * from alert_value;")
    value = cur.fetchall()

    if len(value) == 0:
        cur.execute(f"INSERT INTO alert_value (alert_value) VALUES ({is_triggered});")
    else:
        cur.execute(f"UPDATE alert_value SET alert_value = {is_triggered}, timestamp=\'{datetime.utcnow().replace(microsecond=0)}\';")

    conn.commit()
    conn.close()


def get_alert_value():
    conn = create_connection("./gh_confs.db")
    cur = conn.cursor()

    cur.execute("SELECT * from alert_value;")
    alert_bool = cur.fetchall()

    if (len(alert_bool) > 0):
        return [bool(alert_bool[0][0]), alert_bool[0][1]]


def determine_minute_delta(timestamp):
    current_time = datetime.utcnow()

    date_format = "%Y-%m-%d %H:%M:%S"
    obj_timestamp = datetime.strptime(timestamp, date_format)
 
    timedelta = current_time - obj_timestamp
    return int(timedelta.seconds / 60)


def set_temp_unit(is_celsius: bool):
    conn = create_connection("./gh_confs.db")
    cur = conn.cursor()

    cur.execute("select * from temp_unit;")
    value = cur.fetchall()

    if len(value) == 0:
        cur.execute(f"INSERT INTO temp_unit (is_celsius) VALUES ({is_celsius});")
    else:
        cur.execute(f"UPDATE temp_unit SET is_celsius={is_celsius};")

    conn.commit()
    conn.close()


def get_temp_unit():
    conn = create_connection("./gh_confs.db")
    cur = conn.cursor()

    cur.execute("SELECT * from temp_unit;")
    temp_bool = cur.fetchall()

    if (len(temp_bool) > 0):
        return bool(temp_bool[0][0])
    
    # if we dont have a value in db default to F
    return False


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
    if not get_temp_unit(): # convert to F
        for r in rows:
            current_gh = current_gh + 1
            to_send[str(current_gh)]["tempMax"] = round(r[1] * 9/5) + 32
            to_send[str(current_gh)]["tempMin"] = round(r[3] * 9/5) + 32
            to_send[str(current_gh)]["humidityMax"] = r[2]
            to_send[str(current_gh)]["humidityMin"] = r[4]
    else:
        for r in rows:
            current_gh = current_gh + 1
            to_send[str(current_gh)]["tempMax"] = r[1]
            to_send[str(current_gh)]["tempMin"] = r[3]
            to_send[str(current_gh)]["humidityMax"] = r[2]
            to_send[str(current_gh)]["humidityMin"] = r[4]

    conn.close()
    return json.dumps(to_send)