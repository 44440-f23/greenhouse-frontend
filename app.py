from flask import Flask, render_template, request
from flask_socketio import SocketIO
import serial
import json
from db import Database
from helpers import read_serial, simulate_info, PORT

# init our Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Adjust the URI as needed
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gh_confs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


database = Database(app=app)
database.create_tables()

is_running = False
simulating = False
has_alerted = False

# do we have something plugged in or not


def available_serial_connection(port):
    try:
        ser = serial.Serial(port)
        ser.close()
        return True
    except serial.serialutil.SerialException:
        return False

# root


@app.route('/')
def index():
    temp_unit = database.get_temp_unit()
    return render_template('index.html', isCelsius=temp_unit)


@app.route('/chart')
def chart():
    id = request.args.get('id')
    variable = request.args.get('variable')
    temp_unit = database.get_temp_unit()

    return render_template('chart.html', id=id, variable=variable, isCelsius=temp_unit)


@app.route('/settings')
def settings():
    existing_configs = database.select_current_configs()
    existing_data = json.loads(existing_configs)
    temp_unit = database.get_temp_unit()
    return render_template('settings.html', existing_data=existing_data, isCelsius=temp_unit)


@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        data = request.get_json()
        database.update_existing_configs(data)

    existing_configs = database.select_current_configs()
    existing_data = json.loads(existing_configs)
    return render_template('settings.html', existing_data=existing_data)


@socketio.on("resetAlert")
def resetAlert():
    database.set_alert_value(True)
    print('\nResetting alert, the admin will be alerted again once a variable is out of bounds.\n')


@socketio.on("tempUnitChange")
def tempUnitChange(data):
    database.set_temp_unit(True if data['isCelsius'] else False)
    print('\nTemperate unit set to', 'Celsius' if data['isCelsius'] else 'Fahrenheit', '\n')

# when the client socket connects


@socketio.on("connect")
def connect():
    global is_running
    global simulating

    print("\nSocket connection to client successful.\n")

    if available_serial_connection(PORT):
        # must run the serial reading in the background for it to work
        if not is_running:
            socketio.start_background_task(lambda: read_serial(socket=socketio, database=database))
            is_running = True
            print('\nInitial serial reading started.\n')
        else:
            print('\nAlready reading from serial, will continue to do so.\n')
    else:
        if not simulating:
            # pretend to receive json info
            socketio.start_background_task(lambda: simulate_info(socket=socketio, database=database))
            simulating = True
            print('\nInitial simulation started.\n')
        else:
            print('\nAlready simulating, will continue to do so.\n')

# Event handler for a client disconnecting from the socket
@socketio.on("disconnect")
def disconnect():
    print("\nSocket disconnected.\n")


# Entry point to run the Flask application with Socket.IO support
if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
