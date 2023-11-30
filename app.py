from flask import Flask, render_template, request
from flask_socketio import SocketIO
import serial, json, time, random
import db
import requests

# init our Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

is_running = False
simulating = False
has_alerted = False
alert_interval = 10 # can alert at this interval, minutes

port = "/dev/tty.usbmodem2101"

def celsius_to_fahrenheit(temp):
    return (temp * 9 / 5) + 32

def check_bounds(gh):
    global has_alerted

    gh = json.loads(gh)
    all_configs = json.loads(db.select_current_configs())
    gh_config = all_configs[str(gh["id"])]

    for key in gh_config:
        bound = key[len(key)-3:]
        variable = key[:len(key)-3]

        if bound == "Max":
            if gh[variable] > gh_config[key]:
                if db.get_alert_value()[0] or db.determine_minute_delta(db.get_alert_value()[1]) >= alert_interval:
                    print('\nAlerting admin. No more alerts will be sent.\n')
                    # requests.post("https://maker.ifttt.com/trigger/environment_trigger/with/key/oC8QBG9qOHawiZjEEnt5TN6IanwkOlexvtI1EEvtq7R", json={"value1":gh["id"], "value2":variable, "value3":gh[variable]})
                    db.set_alert_value(False)
                    print(variable, "of value", gh[variable], "from gh", gh["id"], "exceeds", bound, "of", gh_config[key])
        elif bound == "Min":
            if gh[variable] < gh_config[key]:
                if db.get_alert_value()[0] or db.determine_minute_delta(db.get_alert_value()[1]) >= alert_interval:
                    print('\nAlerting admin. No more alerts will be sent.\n')
                    # requests.post("https://maker.ifttt.com/trigger/environment_trigger/with/key/oC8QBG9qOHawiZjEEnt5TN6IanwkOlexvtI1EEvtq7R", json={"value1":gh["id"], "value2":variable, "value3":gh[variable]})
                    db.set_alert_value(False)
                    print(variable, "of value", gh[variable], "from gh", gh["id"], "is below", bound, "of", gh_config[key])

# helper function that reads the basestations serial port 
def read_serial():
    #define the serial port and baud rate

    while True:
        serial_port = serial.Serial(port, baudrate=9600)
        serial_port.flush()

        try:
            # try to read in the serial message
            line = serial_port.readline().decode().strip()
            serial_port.flush()
            # print(line)

            # do light vaildation on if we should try to parse it
            if len(line) != 0 and line[0] == "{":

                check_bounds(line)

                # convert to fahrenheit if user wants
                if not db.get_temp_unit():
                    data = json.loads(line)
                    data['temp'] = celsius_to_fahrenheit(data['temp'])
                    line = json.dumps(data)

                socketio.emit("serial", line)
        except:
            print("failed to read line")

# randomly generate info from random greenhouses
def simulate_info():
    while True:
        gh_ids = list(set([random.randint(1,6) for _ in range(random.randint(1,6))]))

        for id in gh_ids:
            temp = random.randint(18, 23)
            humidity = random.randint(50, 80)   
            soilT = random.randint(20, 24)    
            soilM = random.randint(30, 60) 
            lightS = random.randint(1, 6000) 
            #isCelius true reading in celius 
            #if db.getswitchstatus == false{
            # will only be called when the switch is called
            # do conversion to farenhight 
            # F = (currenttemps)* (9/5) + 32
            # } 
            
            data = json.dumps({
                "id": id,
                "temp": temp,
                "humidity": humidity,
                "soilT": soilT,
                "soilM": soilM,
                "lightS": lightS
            }) 
            check_bounds(data)

            # convert to fahrenheit if user wants
            if not db.get_temp_unit():
                temp_dict = json.loads(data)
                temp_dict['temp'] = celsius_to_fahrenheit(temp_dict['temp'])
                data = json.dumps(temp_dict)

            socketio.emit("serial", data)

        time.sleep(2)

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
    return render_template('index.html', isCelsius=db.get_temp_unit())

@app.route('/chart')
def chart():
    id = request.args.get('id')
    variable = request.args.get('variable')

    return render_template('chart.html', id=id, variable=variable, isCelsius=db.get_temp_unit())

@app.route('/settings')
def settings():
    existing_configs = db.select_current_configs()
    existing_data = json.loads(existing_configs)
    return render_template('settings.html', existing_data=existing_data, isCelsius=db.get_temp_unit())
    
@app.route('/submit_form', methods = ['POST'])
def submit_form():
    if request.method == 'POST':
        data = request.get_json()
        db.update_existing_configs(data)

@app.route('/toggle_endpoint', methods=['POST'])
def handle_toggle():
    data = request.get_json()
    switch_status = data.get('switchStatus')

    # Perform actions based on the switch status
    if switch_status:
        # Switch is toggled ON
        # Perform actions for Fahrenheit mode
        print('Switch is ON - Fahrenheit mode')

    else:
        # Switch is toggled OFF
        # Perform actions for Celsius mode
        print('Switch is OFF - Celsius mode')
        # Add further actions here as needed

    return 'Switch status received'


# when the client socket connects
@socketio.on("connect")
def connect():
    global is_running
    global simulating

    print("\nSocket connection to client successful.\n")

    if available_serial_connection(port):
        # must run the serial reading in the background for it to work
        if not is_running:
            socketio.start_background_task(read_serial)
            is_running = True
            print('\nInitial serial reading started.\n')
        else:
            print('\nAlready reading from serial, will continue to do so.\n')
    else:
        if not simulating:
            # pretend to receive json info
            socketio.start_background_task(simulate_info)
            simulating = True
            print('\nInitial simulation started.\n')
        else:
            print('\nAlready simulating, will continue to do so.\n')

#Event handler for a client disconnecting from the socket
@socketio.on("disconnect")
def disconnect():
    print("\nSocket disconnected.\n")

#Entry point to run the Flask application with Socket.IO support
if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
