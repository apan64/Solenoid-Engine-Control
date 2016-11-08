from pickle import load
import matplotlib.pyplot as plt
with open('logs_2.txt') as f: #We read from a file saved to disc by pyserial-test.py.
    b = load(f)

b = [c for c in b if c!='']
b = [int(k)/10.0 for k in b]
x = [i for i in range(len(b))]


# y = b[:9000]
# x = x[:9000]

plt.figure(figsize=(20,2))
plt.plot(x,b,'r')

plt.show()
# print b