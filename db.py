import sqlite3
from sqlite3 import Error
import json

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
    conn = create_connection("../../../Desktop/gh_confs.db")

    # list of configs generated from the passed in config
    configs = [config["1"], config["2"], config["3"], config["4"], config["5"], config["6"]]
    cur = conn.cursor()

    gh = 1;
    for c in configs: # loop through the configs and use the values of each to update the existing ones in the db
        command = f"UPDATE gh_configs SET tempMax = {c['temp']['max']}, tempMin = {c['temp']['min']}, \
              humidityMax = {c['humidity']['max']}, humidityMin = {c['humidity']['min']} \
                WHERE gh = {str(gh)}"
        cur.execute(command)
        gh = gh + 1; # keep track of the greenhouse that we are on (id)

    conn.commit()
    conn.close()

# grabs current config from db and stores it in json object
def select_current_configs():
    # will need changed to the location of the DB on the linux machine
    conn = create_connection("../../../Desktop/gh_confs.db")
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
    current_gh = 0

    # loop through rows of returned info and store them in there correct spot in the json object
    for r in rows:
        current_gh = current_gh + 1
        to_send[str(current_gh)]["tempMax"] = r[1]
        to_send[str(current_gh)]["humidityMax"] = r[2]
        to_send[str(current_gh)]["tempMin"] = r[3]
        to_send[str(current_gh)]["humidityMin"] = r[4]
        
    conn.close()
    return json.dumps(to_send);
