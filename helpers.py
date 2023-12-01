import serial, json, time, random
from serial import SerialException

alert_interval = 10 # can alert at this interval, minutes
PORT = "/dev/tty.usbmodem2101"

def celsius_to_fahrenheit(temp):
    return (temp * 9 / 5) + 32

def check_bounds(gh, database):
    gh = json.loads(gh)
    all_configs = json.loads(database.select_current_configs())
    gh_config = all_configs[str(gh["id"])]

    for key in gh_config:
        bound = key[len(key)-3:]
        variable = key[:len(key)-3]

        if bound == "Max":
            if gh[variable] > gh_config[key]:
                if database.get_alert_value()[0] or database.determine_minute_delta(str(database.get_alert_value()[1])) >= alert_interval:
                    print('\nAlerting admin. No more alerts will be sent.\n')
                    # requests.post("https://maker.ifttt.com/trigger/environment_trigger/with/key/oC8QBG9qOHawiZjEEnt5TN6IanwkOlexvtI1EEvtq7R", json={"value1":gh["id"], "value2":variable, "value3":gh[variable]})
                    database.set_alert_value(False)
                    print(variable, "of value", gh[variable], "from gh", gh["id"], "exceeds", bound, "of", gh_config[key])
                    return False
        elif bound == "Min":
            if gh[variable] < gh_config[key]:
                if database.get_alert_value()[0] or database.determine_minute_delta(str(database.get_alert_value()[1])) >= alert_interval:
                    print('\nAlerting admin. No more alerts will be sent.\n')
                    # requests.post("https://maker.ifttt.com/trigger/environment_trigger/with/key/oC8QBG9qOHawiZjEEnt5TN6IanwkOlexvtI1EEvtq7R", json={"value1":gh["id"], "value2":variable, "value3":gh[variable]})
                    database.set_alert_value(False)
                    print(variable, "of value", gh[variable], "from gh", gh["id"], "is below", bound, "of", gh_config[key])
                    return False
                
    return True

# helper function that reads the basestations serial port 
def read_serial(socket, database):
    #define the serial port and baud rate

    while True:
        serial_port = serial.Serial(PORT, baudrate=9600)
        serial_port.flush()

        try:
            # try to read in the serial message
            line = serial_port.readline().decode().strip()
            serial_port.flush()
            # print(line)

            # do light vaildation on if we should try to parse it
            if len(line) != 0 and line[0] == "{":

                check_bounds(line, database=database)

                # convert to fahrenheit if user wants
                if not database.get_temp_unit():
                    data = json.loads(line)
                    data['temp'] = celsius_to_fahrenheit(data['temp'])
                    line = json.dumps(data)

                socket.emit("serial", line)
        except SerialException as e:
            print(f"Reading Line threw the exception: {e}")

# randomly generate info from random greenhouses
def simulate_info(socket, database):
    while True:
        gh_ids = list(set([random.randint(1,6) for _ in range(random.randint(1,6))]))

        for gh_id in gh_ids:
            temp = random.randint(18, 23)
            humidity = random.randint(50, 80)   
            soilT = random.randint(20, 24)    
            soilM = random.randint(30, 60) 
            lightS = random.randint(1, 6000) 

            data = json.dumps({
                "id": gh_id,
                "temp": temp,
                "humidity": humidity,
                "soilT": soilT,
                "soilM": soilM,
                "lightS": lightS
            }) 
            check_bounds(data, database=database)

            # convert to fahrenheit if user wants
            if not database.get_temp_unit():
                temp_dict = json.loads(data)
                temp_dict['temp'] = celsius_to_fahrenheit(temp_dict['temp'])
                data = json.dumps(temp_dict)

            socket.emit("serial", data)

        time.sleep(2)