import random
from random import gauss
import json

train_data = []

for i in range(0, 1000):
    temp_max = ((gauss(7, 5)+40.0)/80.0)
    temp_min = ((gauss(1, 5)+40.0)/80.0)
    ff = ((gauss(7, 3.5))/118.0)
    rr = ((gauss(1.6, 1))/10.0)
    sy = random.randint(0, 3)
    humidity = ((gauss(75.0, 10))/100.0)
    thunder = ((gauss(5, 5))/100.0)
    clouds = (gauss(3, 2)/8)           
    condition = 'good'
    a_list = [temp_max, temp_min, ff, rr, sy, humidity, thunder, clouds, condition]
    train_data.append(a_list)

for i in range(0, 1000):
    temp_max = ((gauss(2, 5)+40.0)/80.0)
    temp_min = ((gauss(-2, 5)+40.0)/80.0)
    ff = ((gauss(10, 3.5))/118.0)
    rr = ((gauss(3.6, 1))/10.0)
    sy = random.randint(4, 15)
    humidity = ((gauss(90.0, 10))/100.0)
    thunder = ((gauss(40, 12))/100.0)
    clouds = (gauss(6, 2)/8)           
    condition = 'bad'
    a_list = [temp_max, temp_min, ff, rr, sy, humidity, thunder, clouds, condition]
    train_data.append(a_list)

with open("dezember_new.txt", "w") as thefile:
    for items in train_data:
        thefile.writelines(",".join(map(str, items)) + "\n")
