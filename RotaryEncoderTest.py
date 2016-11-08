import serial
from pickle import dump, load
arduino = serial.Serial('COM4', 9600, timeout=0.7) # Some pyserial magic lets us read directly from the Serial port.

def read_stuff(readings):
    """read_stuff(X) takes the first X readings from the Serial monitor.
    Serial prints a "distance, horizontal angle, vertical angle" string
    """
    test = []
    while len(test)<readings:
        data = arduino.readline()[:-2] # the last bit gets rid of the '\n' chars that Serial.println() method appends to the back of each new line.
        if data == None:
            print len(test), len(test) # for debug purposes
        else:
            print len(test), data       
            test.append(data)          # append useful data to our list
    return test

# We store the raw data in a file. data-processing-tuples does the processing.

a = read_stuff(40000)
print a
f = open('logs_2.txt','w')
dump(a, f)
f.close()
