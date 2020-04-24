#!/usr/bin/env python
import sys
import subprocess
import time
import flickrapi
import urllib.request
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# set up gpio pins:
trig = 23
echo = 24
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

def get_distance():
    # initialize trig to low
    GPIO.output(trig, GPIO.LOW)
    time.sleep(1)

    # trigger sensor with 10us pulse
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig, GPIO.LOW)

    # wait for echo
    while (GPIO.input(echo) == 0):
        start = time.time()
        
    while (GPIO.input(echo) == 1):
        end = time.time()
        
    # calculate time for echo to return
    # divide by 2 since time measurement is for travelling back and forth
    time_diff = (end - start) / 2

    # calculate distance: distance = time * speed of sound
    # speed of sound = 343 m/s = 34300 cm/s
    distance = time_diff * 34300
    distance = round(distance, 1)

    return distance


def get_photos():
    FLICKR_KEY = 'bae0ead7cafdef8d0685974c051ae147'
    FLICKR_SECRET = '2f820fa0a9f15201'
    USER_ID = "187939967@N04"

    flickr = flickrapi.FlickrAPI(FLICKR_KEY, FLICKR_SECRET, cache=True)
    # request photos from user profile (my profile)
    # url_c: URL of medium, 800 on longest size image
    photos = flickr.walk(user_id=USER_ID, extras='url_c')
    
    # save photos to local images folder
    for i, photo in enumerate(photos):
        url = photo.get('url_c')
        file_name = "/home/pi/DeskAssistant/images/" + str(i) + ".jpg"
        urllib.request.urlretrieve(url, file_name)   


def main():
    # run_driver.sh - runs MagicMirror software in the background
    subprocess.call(["./run_driver.sh"])
    # start Alexa in background
    subprocess.Popen(["./alexa.sh"])
    
    # download slideshow photos from Flickr
    get_photos()
    
    # monitor states: 1 = MagicMirror, 2 = slideshow, 3 = off
    monitor_state = 1 
    while True:
        # get reading in cm from distance sensor
        distance = get_distance()
        
        # when hand is placed close to monitor (<= 7.0 cm), it will change states
        if (distance <= 7.0 and monitor_state == 3):
            monitor_state = 1
            subprocess.call(["./monitor_on.sh"])    
        elif (distance <= 7.0 and monitor_state == 1):
            monitor_state = 2
            subprocess.Popen(["./slideshow.sh"])
        elif (distance <= 7.0 and monitor_state == 2):
            monitor_state = 3
            subprocess.Popen(["./kill_slideshow.sh"])
            subprocess.call(["./monitor_off.sh"])   


if __name__ == "__main__":
    main()