# bikedashcam
A dashcam for bicycles

Both the bash script delete_oldest_.h264.sh and python 2 file dashcamcorder.py 
should also be located in /home/pi and made executable (chmod +x filename)

If you want it to run on boot, add...

/bin/python /home/pi/dashcamcorder.py &

...to the end of your rc.local file with

sudo nano /etc/rc.local

You could use systemd instead, but then you don't get the same console output which is useful on the bike to see what's happening.

If you're wondering why it's in Python 2, it's because it's an evolution of raspicamcorder which was written in Python 2.
It should be relatively easy to make it Python 3, but I'd rather spend my time making it work the way I want than satisfying the fussy requirements people with issues.

To my mind it makes no sense to start a completely new project in Python 2 these days unless it needs to interact with legacy Python 2 stuff. Well this IS legacy Python 2 stuff, not a completely new project.

