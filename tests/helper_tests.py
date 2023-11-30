import unittest
from unittest.mock import patch
from flask import Flask
from db import Database, gh_configs, alert_value, temp_unit
import json
from test_data import test_config
from helpers import check_bounds, read_serial, simulate_info, celsius_to_fahrenheit

class test_helper_functions(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for testing
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy modification tracking
        self.db = Database(self.app)
        self.db.create_tables()
 
        with self.app.app_context():
            self.db.set_temp_unit(True)
            self.db.update_existing_configs(test_config)
            self.db.set_alert_value(True)
            


        
    def tearDown(self):
        with self.app.app_context():
            gh_configs.query.delete()
            alert_value.query.delete()
            temp_unit.query.delete()
            self.db.db.session.commit()

    @patch('builtins.print')
    def test_check_bounds(self, mock_print):
        below_config = '{"id": 1, "temp": 32, "humidity": 52}'
        below_val = check_bounds(below_config, database=self.db)

        self.assertEqual(below_val, False)
        self.db.set_alert_value(True)

        above_config = '{"id": 1, "temp": 100, "humidity": 100}'
        above_val = check_bounds(above_config, database=self.db)

        self.assertEqual(above_val, False)
        self.db.set_alert_value(True)

        in_range_config = '{"id": 1, "temp": 55, "humidity": 62}'
        in_val = check_bounds(in_range_config, database=self.db)

        self.assertEqual(in_val, True)

    def test_celsius_to_fahrenheit(self):
        val = celsius_to_fahrenheit(50)
        self.assertEqual(val, 122)

        val = celsius_to_fahrenheit(0)
        self.assertEqual(val, 32)

        val = celsius_to_fahrenheit(100)
        self.assertEqual(val, 212)
