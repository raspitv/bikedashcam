stat --printf='%Y %n\0' /home/pi/*.h264 | sort -z | sed -zn '1s/[^ ]\{1,\} //p' |  xargs -0 rm
