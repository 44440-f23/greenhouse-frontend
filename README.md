# greenhouse-frontend

## Overview

The current state of the project relies on real-time sensor data through a serial connection. For it to work as expected, you need to have either an ESP-32 sending json to COM port 5, or some phony json being sent every once in a while. 

When trying to run the app the first time, it may fail, but it seems to always work on the second try. I think it is an issue with reading the serial port from the start, maybe the garbage characters that are sent from our ESP-32?

## Command Line References

* Install dependencies (in your virtual environment)
```bash
pip install -r requirements.txt
```

* Run app on localhost
```bash 
python app.py
```

* Installing a new python package
```bash
pip install *package*
```

* If you installed a new package, be sure to update the requirements text file
```bash
pip freeze > requirements.txt
```

## Downloading SQLite
Follow this tutorial: https://www.sqlitetutorial.net/download-install-sqlite/

To run SQLite in any directory on your Windows machine, you must add it to your PATH.
1. Type 'environ' in the task bar and click 'Edit the system environment variables'
2. Click "Environment Variables..." button
3. Under the User variables section at the top, click on the "Path" variable, then Edit
4. From here you will want to click "New" and type the path to the SQLite files (if you followed the tutorial this should be C:\sqlite)

* Here are commands to create a db on your local machine. 
* It will be created in the directory where they are ran.

```bash
# start sqlite3
sqlite3

# command to create db
.open gh_confs.db

# command to create table
CREATE TABLE gh_configs (
gh INT,
tempMax INT,
humidityMax INT,
tempMin INT,
humidityMin INT
);

CREATE TABLE temp_unit (is_celsius BOOLEAN);
```
