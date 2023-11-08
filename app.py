from flask import Flask, render_template, request
from flask_socketio import SocketIO
import serial, json, time, random
import db

# init our Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

is_running = False
simulating = False

port = "/dev/tty.usbmodem2101"

# helper function that reads the basestations serial port 
def read_serial():
    #define the serial port and baud rate

    while True:
        # reading constantly creates inconsistencies. This seems fairly robust
        # might run into issues with messages piling up? 
        # try to grab the line and emit it

        serial_port = serial.Serial(port, baudrate=9600)
        serial_port.flush()

        try:
            line = serial_port.readline().decode().strip()
            serial_port.flush()
            print(line)
            if len(line) != 0 and line[0] == "{":
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

            data = json.dumps({
                "id": id,
                "temp": temp,
                "humidity": humidity,
                "soilT": soilT,
                "soilM": soilM,
                "lightS": lightS
            })

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
    return render_template('index.html', title="Flaskaroo")

@app.route('/chart')
def chart():
    id = request.args.get('id')
    variable = request.args.get('variable')

    return render_template('chart.html', id=id, variable=variable)

@app.route('/settings')
def settings():
    return render_template('settings.html')#possible sending of the mins and maxs later

# when the client socket connects
@socketio.on("connect")
def connect():
    global is_running
    global simulating
    
    print("\nSocket connection to client successful.\n")

    # grabs current settings config from db
    current_confs = db.select_current_configs()
    socketio.emit("config", current_confs)

    if available_serial_connection(port):
        # must run the serial reading in the background for it to work
        if not is_running:
            socketio.start_background_task(read_serial)
            is_running = True
            print('\nInitial serial reading started.\n')
        else:
            print('\Already reading from serial, will continue to do so.\n')
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
    socketio.run(app)