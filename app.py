from flask import Flask, render_template
from flask_socketio import SocketIO
import serial, json

# init our Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# helper function that reads the COM5 serial port 
def read_serial():
    serial_port = serial.Serial('COM5', baudrate=9600)
    while True:
        # serial is wacky, sometimes it doesn't know how to decode() so this is just how it is for now
        try:
            data = serial_port.readline().decode().strip()
            parsed = json.loads(data)
            print(parsed)
            socketio.emit("serial", parsed)
        except:
            data = serial_port.readline().strip()
            parsed = json.loads(data)
            socketio.emit("serial", parsed)

# root
@app.route('/')
def index():
    return render_template('index.html', title="Flaskaroo")

# when the client socket connects
@socketio.on("connect")
def connect():
    print("\nSocket connection to client successful.\n")

    # must run the serial reading in the background for it to work
    socketio.start_background_task(read_serial)

@socketio.on("disconnect")
def disconnect():
    print("\nSocket disconnected.\n")

if __name__ == '__main__':
    socketio.run(app)