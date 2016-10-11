from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

def read_data():
    with open("/Users/Ben/workspace/weather/weather/app/training_data_set/january_new.txt", "r") as f:
#        lines = f.readlines()
        lines=[line.strip() for line in f.readlines()]
 
    
    lines=[line.split(",") for line in lines if line] 
    class1=np.array([line[:7] for line in lines if "good" in line[-1]], dtype=np.float) 
    class2=np.array([line[:7] for line in lines if "good" not in line[-1]], dtype=np.float)
     
    return class1, class2
    
     
def main():
   
    class1, class2=read_data()
   
    mean1=np.mean(class1, axis=0)
    mean2=np.mean(class2, axis=0)
     
    #calculate variance within class
    Sw=np.dot((class1-mean1).T, (class1-mean1))+np.dot((class2-mean2).T, (class2-mean2))
     
    #calculate weights which maximize linear separation
    w=np.dot(np.linalg.inv(Sw), (mean2-mean1))
   
    print "vector of max weights", w
    #projection of classes on 1D space
    plt.plot(np.dot(class1, w), [0]*class1.shape[0], "bo", label="good")
    plt.plot(np.dot(class2, w), [0]*class2.shape[0], "go", label="bad")
    plt.legend()
    
    plt.show()
   
main()
