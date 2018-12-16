# bikedashcam
A dashcam for bicycles

Both the bash script delete_oldest_.h264.sh and python 2 file dashcamcorder.py 
should also be located in /home/pi and made executable (chmod +x filename)

If you want it to run on boot, add...

/bin/python /home/pi/dashcamcorder.py &

...to the end of your rc.local file with

sudo nano /etc/rc.local

You could use systemd but then you don't get the same console output which is useful on the bike to see what's happening.

