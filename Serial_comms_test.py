from time import sleep
import serial

arduino = serial.Serial('COM4', 9600, timeout=0.5) # Some pyserial magic lets us read directly from the Serial port.

functioning = True
while functioning:
    if raw_input != 'stop':
        arduino.write(raw_input('--> ').encode('UTF-8'))
        # sleep(1.0)
        # if arduino.readline():
        # print arduino.readline()[:-2]
    else:
        functioning = False
