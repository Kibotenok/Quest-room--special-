# Created by Antropov N.A.
# Autostart
err=1
while err==1:
#if(1==1):
    try:
        exec(open('/home/pi/Desktop/Quest/MainProcess.py').read())
        print("Runned")
        err=0;
    except:
        print("Eroor in running")
        err=1
        pass
