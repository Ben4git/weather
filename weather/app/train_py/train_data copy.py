from random import gauss
import json

train_data = []

for i in range(0, 1000):
    temperature = ((gauss(18, 3)+40.0)/80.0)
    rrp = ((gauss(70, 15))/100.0)
    ss = ((gauss(15, 9))/60.0)
    ff = ((gauss(7.2, 3))/118.0)
    humidity = ((gauss(80, 10))/100.0)
    pressure = ((gauss(1000, 7)-970)/70)
    condition = 'bad'
    a_list = [temperature, rrp, ss, ff, humidity, pressure, condition]
    train_data.append(a_list)

for i in range(0, 1000):
    temperature = ((gauss(22, 3)+40.0)/80.0)
    rrp = ((gauss(30, 15))/100.0)
    ss = ((gauss(45, 9))/60.0)
    ff = ((gauss(7.2, 3))/118.0)
    humidity = ((gauss(50, 10))/100.0)
    pressure = ((gauss(1020, 7)-970)/70)
    condition = 'good'
    a_list = [temperature, rrp, ss, ff, humidity, pressure, condition]
    train_data.append(a_list)

with open("a_data.txt", "w") as thefile:
    for items in train_data:
        thefile.writelines(",".join(map(str, items)) + "\n")

