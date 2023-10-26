from flask import Flask, render_template
from flask_socketio import SocketIO
import serial, json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

def read_serial():
    serial_port = serial.Serial('COM5', baudrate=9600)
    while True:
        try:
            data = serial_port.readline().decode().strip()
            parsed = json.loads(data)
            print(parsed)
            socketio.emit("serial", parsed)
        except:
            data = serial_port.readline().strip()
            parsed = json.loads(data)
            socketio.emit("serial", parsed)

@app.route('/')
def index():
    return render_template('index.html', title="Flaskaroo")

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