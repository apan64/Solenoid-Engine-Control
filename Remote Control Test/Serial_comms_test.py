from time import sleep
import serial

# arduino = serial.Serial('COM7', 9600, timeout=0.5, dsrdtr = True) # Some pyserial magic lets us read directly from the Serial port.
arduino = serial.Serial()
arduino.baudrate = 9600
arduino.port = 'COM7'

arduino.dtr = 0

arduino.open()

# arduino.setDTR(0)
# arduino.open()

functioning = True
while functioning:
    if raw_input != 'stop':
        arduino.write(raw_input('--> ').encode('UTF-8'))
        # sleep(0.6)
        # if arduino.readline():
        #     print arduino.readline()[:-2]
    else:
        functioning = False
        arduino.close()
