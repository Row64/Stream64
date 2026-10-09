import os
import math
import time
from kafka import KafkaProducer
    
def main():
    
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    print("----- Generating Kafka Test Signals -----")
    
    M_2PI = 6.28318530718
    circleDiv = 256
    aStep = M_2PI / circleDiv
    cx = -97.29451
    cy = 39.908065
    rad = 9.4 
    ang = 0
    while True:
        xp = cx+rad*math.cos(ang)
        yp = cy+rad*math.sin(ang)
        val = "["  + str(xp) + ","+str(yp)+"]"
        producer.send('example_loc', val.encode())
        time.sleep(.015) # update rate in seconds
        ang += aStep

    # Ensure all messages are sent before exiting
    producer.flush()

main()