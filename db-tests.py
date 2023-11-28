import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from flask import Flask
from db import Database, gh_configs, alert_value, temp_unit
import json

class test_db_functions(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for testing
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy modification tracking
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

        test_config = {
            "1" : {
            "tempMax": 60,
            "tempMin": 40,
            "humidityMax": 70,
            "humidityMin": 60,
            },
            "2" : {
            "tempMax": 80,
            "tempMin": 50,
            "humidityMax": 90,
            "humidityMin": 80,
            },
            "3" : {
            "tempMax": 80,
            "tempMin": 50,
            "humidityMax": 90,
            "humidityMin": 80,
            },
            "4" : {
            "tempMax": 80,
            "tempMin": 50,
            "humidityMax": 90,
            "humidityMin": 80,
            },
            "5" : {
            "tempMax": 80,
            "tempMin": 50,
            "humidityMax": 90,
            "humidityMin": 80,
            },
            "6" : {
            "tempMax": 80,
            "tempMin": 50,
            "humidityMax": 90,
            "humidityMin": 80,
            }
        }
        with self.app.app_context():
            result = self.db.update_existing_configs(test_config)
            updated = gh_configs.query.filter_by(gh=1).first()

        self.assertEqual(updated.tempMax, 60)
        self.assertEqual(updated.tempMin, 40)
        self.assertEqual(updated.humidityMax, 70)
        self.assertEqual(updated.humidityMin, 60)

    @patch("db.sqlite3.connect")
    def test_get_all_gh_configs(self, mock_connect):
        mock_cur = mock_connect.return_value.cursor.return_value

        mock_cur.fetchall.return_value = [(1, 32, 80, 20, 30),
                                            (2, 32, 80, 22, 30),
                                            (3, 32, 80, 20, 30),
                                            (4, 32, 80, 20, 30),
                                            (5, 32, 80, 22, 30),
                                            (6, 32, 80, 22, 30)]
        
        configs = self.db.select_current_configs()
        self.assertEqual(len(json.loads(configs)), 6)


if __name__ == '__main__':
    unittest.main()