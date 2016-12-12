import serial

arduino = serial.Serial()
arduino.baudrate = 9600
arduino.port = 'COM7'

arduino.dtr = 0

arduino.open()

functioning = True
while functioning:
    if raw_input != 'stop':
        arduino.write(raw_input('--> ').encode('UTF-8'))
    else:
        functioning = False
        arduino.close()
