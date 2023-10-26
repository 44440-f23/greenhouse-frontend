from flask import Flask, render_template
from flask_socketio import SocketIO
import serial, json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Function to read data from a serial port
def read_serial():
    #define the serial port and baud rate
    serial_port = serial.Serial('COM5', baudrate=9600)
    while True:
        try:
            #read a lie of data from the serial port and decode it as a string
            data = serial_port.readline().decode().strip()

            #parse that data as JSON
            parsed = json.loads(data)
            print(parsed)

            #Emit the parsed data to connected clients using Socket.IO
            socketio.emit("serial", parsed)

        except:
            #Handle exeptions if JSON parsing fails
            data = serial_port.readline().strip()
            parsed = json.loads(data) #this might cause a problem in the future
            socketio.emit("serial", parsed)


#Define a rout for the main page
@app.route('/')
def index():
    return render_template('index.html', title="Flaskaroo")

#Event Handler for a client connecting to the socket
@socketio.on("connect")
def connect():
    print("\nSocket connection to client successful.\n")

    # must run the serial reading in the background for it to work
    #to aviod blocking the main server
    socketio.start_background_task(read_serial)

#Event handler for a client disconnecting from the socket
@socketio.on("disconnect")
def disconnect():
    print("\nSocket disconnected.\n")

#Entry point to run the Flask application with Socket.IO support
if __name__ == '__main__':
    socketio.run(app)