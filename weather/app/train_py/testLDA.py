from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import json

with open("/Users/Ben/Desktop/a_data.txt", "r") as f:
    lines = f.readlines()
    
lines=[line.split(",") for line in lines if line]
print([line[:6] for line in lines])
class1= [line[:6] for line in lines if "good" in line[-1]]
class2= [line[:6] for line in lines if "good" not in line[-1]]

print class1
print class2
#    return class1, class2
