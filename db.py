import sqlite3
import json
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class gh_configs(db.Model):
    gh = Column(Integer, primary_key=True)
    tempMax = Column(Integer, default=0)
    tempMin = Column(Integer, default=0)
    humidityMax = Column(Integer, default=0)
    humidityMin = Column(Integer, default=0)

class alert_value(db.Model):
    alert_value = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, primary_key=True)

class temp_unit(db.Model):
    is_celsius = Column(Boolean, primary_key=True, default=False)

class Database:

    def __init__(self, app, db_path="./gh_confs.db"):
        self.db_path = db_path
        self.db = db
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app
        self.db.init_app(app)

    def create_tables(self):
        with self.app.app_context():
            self.db.create_all()

    # update existing configs based on gather info from settings page
    # requires a complete config file even if only some values are changed
    def update_existing_configs(self, config):
        # will need changed to the location of the DB on the linux machine
        with self.app.app_context():

            try:
                # list of configs generated from the passed in config
                configs = [config["1"], config["2"], config["3"], config["4"], config["5"], config["6"]]
                
                for gh, c in enumerate(configs, start=1): # loop through the configs and use the values of each to update the existing ones in the db
                    existing_config = gh_configs.query.filter_by(gh=str(gh)).first()

                    if existing_config is None:
                        print("We are inserting")
                        new_config = gh_configs(gh=str(gh), tempMax=c['tempMax'], tempMin=c['tempMin'], humidityMax=c['humidityMax'], humidityMin=c['humidityMin'])
                        self.db.session.add(new_config)

                    else:
                        print("We are updating")
                        existing_config.tempMax = c['tempMax']
                        existing_config.tempMin = c['tempMin']
                        existing_config.humidityMax = c['humidityMax']
                        existing_config.humidityMin = c['humidityMin']

                self.db.session.commit()

                print("Update / Insert Complete")
                
            except sqlite3.Error as e:
                print(e)


    def set_alert_value(self, is_triggered: bool):
        print('\nSETTING ALERT TO', is_triggered, '\n')
        with self.app.app_context():

            al_val = alert_value.query.first();

            if al_val is None:
                new = alert_value(alert_value=is_triggered, timestamp=datetime.utcnow().replace(microsecond=0))
                self.db.session.add(new)
            else:
                al_val.alert_value = is_triggered
                al_val.timestamp = datetime.utcnow().replace(microsecond=0)
                
            self.db.session.commit()


    def get_alert_value(self):
        with self.app.app_context():
            current = alert_value.query.first()

            if current is not None:
                return [bool(current.alert_value), current.timestamp]


    def determine_minute_delta(self, timestamp):
        current_time = datetime.utcnow()

        date_format = "%Y-%m-%d %H:%M:%S"
        obj_timestamp = datetime.strptime(timestamp, date_format)
    
        timedelta = current_time - obj_timestamp
        return int(timedelta.seconds / 60)


    def set_temp_unit(self, is_celsius: bool):
        with self.app.app_context():
            current = temp_unit.query.first()

            if current is None:
                new = temp_unit(is_celsius=is_celsius)
                self.db.session.add(new)
            else:
                current.is_celsius = is_celsius

            self.db.session.commit()

    def get_temp_unit(self):
        with self.app.app_context():
            current = temp_unit.query.first()

            if (current is not None):
                return bool(current.is_celsius)
        
        # if we dont have a value in db default to F
        return False


    # grabs current config from db and stores it in json object
    def select_current_configs(self):
        # will need changed to the location of the DB on the linux machine
        with self.app.app_context():
            current = gh_configs.query.all()

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
            # if the unit is Fahrenheit convert it to that before we display it
            if not self.get_temp_unit(): # convert to F
                for r in current:
                    current_gh = current_gh + 1
                    to_send[str(current_gh)]["tempMax"] = round(r.tempMax * 9/5) + 32
                    to_send[str(current_gh)]["tempMin"] = round(r.tempMin * 9/5) + 32
                    to_send[str(current_gh)]["humidityMax"] = r.humidityMax
                    to_send[str(current_gh)]["humidityMin"] = r.humidityMin
            else:
                for r in current:
                    current_gh = current_gh + 1
                    to_send[str(current_gh)]["tempMax"] = r.tempMax
                    to_send[str(current_gh)]["tempMin"] = r.tempMin
                    to_send[str(current_gh)]["humidityMax"] = r.humidityMax
                    to_send[str(current_gh)]["humidityMin"] = r.humidityMin

        return json.dumps(to_send)