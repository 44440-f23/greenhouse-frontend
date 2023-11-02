from flask import Flask, render_template
from flask_socketio import SocketIO
import serial, json, time, random

# init our Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

port = "/dev/tty.usbmodem2101"

# helper function that reads the COM5 serial port 
def read_serial():
    #define the serial port and baud rate
    serial_port = serial.Serial(port, baudrate=9600, timeout=2)

    while True:
        # serial is wacky, sometimes it doesn't know how to decode() so this is just how it is for now
        line = serial_port.readline().decode().strip()

        if len(line) != 0 and line[0] == "{":
            try:
                socketio.emit("serial", line)
            except:
                print("failed to parse")

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

@app.route('/other')
def other():
    return render_template('other.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')#possible sending of the mins and maxs later


# when the client socket connects
@socketio.on("connect")
def connect():
    print("\nSocket connection to client successful.\n")

    if available_serial_connection(port):
        # must run the serial reading in the background for it to work
        socketio.start_background_task(read_serial)
    else:
        # pretend to receive json info
        socketio.start_background_task(simulate_info)

#Event handler for a client disconnecting from the socket
@socketio.on("disconnect")
def disconnect():
    print("\nSocket disconnected.\n")

#Entry point to run the Flask application with Socket.IO support
if __name__ == '__main__':
    socketio.run(app)