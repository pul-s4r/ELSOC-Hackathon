import serial

def init_connection(port, baud):
    arduino = serial.Serial(port, baud, timeout=0.1)
    return arduino

def read_int(arduino):
    data_raw = arduino.readline()[:-2]
    data_str = data_raw.decode("utf-8")

    try:
        data = int(data_str)
    except ValueError:
        data = None
    if data:
        print(data)
        return data

    return None
