#!/usr/bin/env python2.7
import RPi.GPIO as GPIO
from subprocess import call
import subprocess
from time import sleep
import time
import sys
import os

GPIO.setmode(GPIO.BCM)

# GPIO 13 (lower button) & 6 (upper button) set up as input, pulled up
# Both ports are wired to connect to GND on button press.
# So set up falling edge detection for both

GPIO.setup( 6, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Record button
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Stop, close, shutdown button

SDcard_threshold = 85  # % of SD card above which we'll delete oldest .h264 files
recording = 0
stop_pressed = 0
vid_rec_num = "vid_rec_num.txt"   
vid_rec_num_fp ="/home/pi/vid_rec_num.txt" # need full path if run from rc.local
base_vidfile = "raspivid -t 300000 -hf -o /home/pi/video"  # default 5 minutes

time_off = time.time()

def write_rec_num():
    vrnw = open(vid_rec_num_fp, 'w')
    vrnw.write(str(rec_num))
    vrnw.close()

def start_recording(rec_num):
    global recording
    global stop_pressed    
    if recording == 0:
        vidfile = base_vidfile + str(rec_num).zfill(5)
        vidfile += ".h264  -fps 25 -b 15000000 -vs"   # -vs is image stabilisation
        print "starting recording\n%s" % vidfile
        time_now = time.time()
        if (time_now - time_off) >= 0.3:
            recording = 1
            space_used()        # check there's space for the file
            call ([vidfile], shell=True)
    recording = 0               # only kicks in if the video runs the full period
    
    if stop_pressed == 0:
        #sleep(1)               # probably can be shortened or eliminated
        record_pressed(7)       # use 7 instead of 6 to help ID source of call

def stop_recording():
    global recording
    global time_off
    global stop_pressed
    stop_pressed = 1
    time_off = time.time()
    print "stopping recording"
    call (["pkill raspivid"], shell=True)
    recording = 0
    space_used()        # display space left on recording drive

def remove_a_file():    # command fails directly but works fine as a bash script
    #cmd = "stat --printf='%Y %n\0' /home/pi/*.h264 | sort -z | sed -zn '1s/[^ ]\{1,\} //p' |  xargs -0 rm"
    cmd = '/home/pi/delete_oldest_.h264.sh'
    call ([cmd], shell=True)

def space_used():    # function to display space left on recording device
    output_df = subprocess.Popen(["df", "-Ph"], stdout=subprocess.PIPE).communicate()[0]

    it_num = 0
    for line in output_df.split("\n"):
        line_list = line.split()
        if it_num == 1:
            storage = line_list
        it_num += 1
    print "Card size: %s Used: %s  Available: %s  Percent used: %s  SD Threshold: %d" % (storage[1], storage[2], storage[3], storage[4], SDcard_threshold)
    percent_used = int(storage[4][0:-1])
    if percent_used > SDcard_threshold:
        print "SD card %s full. Not enough space left! Removing oldest .h264 file" % storage[4]
        remove_a_file()  # call our function to make some space on the card
        space_used()     # call this function recursively until enough space on card

# threaded callback function 
# increments variable rec_num for filename and starts recording
def record_pressed(channel):
    global rec_num
    global stop_pressed
    stop_pressed = 0
    print channel
        
    time_now = time.time()
    if (time_now - time_off) >= 0.3:
        if channel == 7:
            print "Continuing recording in the next file..."
        else:
            print "Record button pressed"
        rec_num += 1
        if recording == 0:
            write_rec_num()
            start_recording(rec_num)

def shutdown():
    print "shutting down now"
    stop_recording()
    GPIO.cleanup()
    os.system("sudo halt")
    sys.exit()

print "Make sure you have a button connected so that when pressed"
print "it will connect GPIO port 6 (pin 31) to GND (pin 25)\n"
print "You will also need a second button connected so that when pressed"
print "it will connect GPIO port 13 (pin 33) to GND (pin 39)\n"

space_used()    # check we've got some space on the SD card

# when a falling edge is detected on port 6 record() will be run
GPIO.add_event_detect(6, GPIO.FALLING, callback=record_pressed)

        # check rec_num from file
try:
    directory_data = os.listdir("/home/pi")
    if vid_rec_num in directory_data:

        # read file vid_rec_num, make into int() set rec_num equal to it
        vrn = open(vid_rec_num_fp, 'r')
        rec_num = int(vrn.readline())
        print "rec_num is %d" % rec_num
        vrn.close() 
   
    else:           # if file doesn't exist, create it
        rec_num = 0
        write_rec_num()

except:
    print("Problem listing /home/pi")
    GPIO.cleanup()
    sys.exit()
    
try:
    while True:
          # this will run until button on GPIO13 is pressed, then
          #   if pressed short,     stop recording
          #   if pressed long,      close program
          #   if pressed very long, shutdown Pi gracefully
        print "Waiting for button press"
        GPIO.wait_for_edge(13, GPIO.FALLING)
        print "Stop button pressed"
        stop_recording()

          # poll GPIO 13 bottom button at 20 Hz for 3 seconds
          # if still pressed at the end of that time period, shut down
          # if released at all, break
        for i in range(60):
            if GPIO.input(13):
                break
            sleep(0.05)

        if 25 <= i < 58:              # if released between 1.25 & 3s close prog
            print "Closing program"
            GPIO.cleanup()
            sys.exit()

        if not GPIO.input(13):
            if i >= 59:
                shutdown()

except KeyboardInterrupt:
    stop_recording()
    GPIO.cleanup()        # clean up GPIO on CTRL+C exit


# it's now in an executable file called delete_oldest_.h264.sh
#cmd = "stat --printf='%Y %n\0' /home/pi/*.h264 | sort -z | sed -zn '1s/[^ ]\{1,\} //p' |  xargs -0 rm"
#call ([cmd], shell=True)

#### Quality VS length ###
# on long clips at max quality you may get dropouts
# -w 1280 -h 720 -fps 25 -b 3000000 
# seems to be low enough to avoid this 
