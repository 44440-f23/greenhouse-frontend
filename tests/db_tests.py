import unittest
from datetime import datetime, timedelta
from flask import Flask
from db import Database, gh_configs, alert_value, temp_unit
import json
from test_data import test_config

class test_db_functions(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for testing
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = Database(self.app)
        self.db.create_tables()

        
    def tearDown(self):
        with self.app.app_context():
            gh_configs.query.delete()
            alert_value.query.delete()
            temp_unit.query.delete()
            self.db.db.session.commit()


    def test_set_alert_value(self):
        with self.app.app_context():
            self.db.set_alert_value(False)
            self.db.db.session.commit()
            val = alert_value.query.first()
            self.assertEqual(val.alert_value, False)

            self.db.set_alert_value(True)
            self.db.db.session.commit()
            val = alert_value.query.first()
            self.assertEqual(val.alert_value, True)

    def test_get_alert_value(self):
        with self.app.app_context():
            val = self.db.get_alert_value()
            self.assertEqual(val, None)

            self.db.set_alert_value(False)
            self.db.db.session.commit()

            val = self.db.get_alert_value()
            self.assertEqual(val[0], False)
            self.assertEqual(type(val[1]), datetime)

    def test_determine_time_delta(self):
        current = datetime.utcnow()
        ten_from_current = current + timedelta(minutes=-10)
        one_hundred_from_current = current + timedelta(minutes=-100)

        print(ten_from_current.replace(microsecond=0))
        val = self.db.determine_minute_delta(str(ten_from_current.replace(microsecond=0)))
        self.assertEqual(val, 10)
        val = self.db.determine_minute_delta(str(one_hundred_from_current.replace(microsecond=0)))
        self.assertEqual(val, 100)


    def test_set_temp_unit(self):
        with self.app.app_context():
            self.db.set_temp_unit(True)
            self.db.db.session.commit()
            val = temp_unit.query.first()
            self.assertEqual(val.is_celsius, True)

            self.db.set_temp_unit(False)
            self.db.db.session.commit()
            val = temp_unit.query.first()
            self.assertEqual(val.is_celsius, False)

    def test_get_temp_unit(self):
        with self.app.app_context():
            val = self.db.get_temp_unit()
            self.assertEqual(val, False)

            self.db.set_temp_unit(True)
            self.db.db.session.commit()
            val = self.db.get_temp_unit()
            self.assertEqual(val, True)

            self.db.set_temp_unit(False)
            self.db.db.session.commit()
            val = self.db.get_temp_unit()
            self.assertEqual(val, False)

    def test_insert_config(self):

        with self.app.app_context():
            self.db.update_existing_configs(test_config)
            updated = gh_configs.query.filter_by(gh=1).first()

        self.assertEqual(updated.tempMax, 60)
        self.assertEqual(updated.tempMin, 40)
        self.assertEqual(updated.humidityMax, 70)
        self.assertEqual(updated.humidityMin, 60)

    def test_get_all_gh_configs(self):

        with self.app.app_context():
            self.db.update_existing_configs(test_config)
            current = self.db.select_current_configs()
        
        self.assertEqual(len(json.loads(current)), 6)


if __name__ == '__main__':
    unittest.main()