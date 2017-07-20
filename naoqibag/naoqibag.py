import qi
import argparse
import sys
import time
import threading
import os
import functools

from naoqi import ALProxy
import Image

keys_list = []

def readKeysFile(keys_file, memory_service):
    for line in keys_file:
        key = line.strip()

        if key[0] == '#':
            print "Skipped comment: ", key
        elif key[0:7] == 'include':
            new_keys_filename = key[8:len(key)]
            try:
                print "Opening new keys file:", new_keys_filename
                new_keys_file = open(new_keys_filename, "r")
                #Recursion!
                readKeysFile(new_keys_file, memory_service)
            except IOError:
                print "Error opening keys file:", new_keys_filename
        else:
            keys_list.append(key)


def onEvent(pip, pport, value):
    global camera_enabled
    global camera_frame_rate
    print "value: ", value 
    if (value==0):
        camera_enabled = 0
    else:
        camera_enabled = 1
        camera_frame_rate = value
        #create a thead that monitors directly the signal
        camMonitorThread = threading.Thread(target = cameraMonitorThread, args = (pip, pport, camera_frame_rate))
        camMonitorThread.start()        

def cameraMonitorThread (pip, pport, rate):
    global camera_enabled
    global current_log_dir
    camera_log_dir = os.path.join(current_log_dir, "kTopCamera")
    if not os.path.exists(camera_log_dir):
        os.makedirs(camera_log_dir)

    print 'Starting recording camera @%.2fHz'%rate
    camProxy = ALProxy("ALVideoDevice", pip, pport)
    camera = 0
    resolution = 2    # VGA
    colorSpace = 11   # RGB
    videoClient = camProxy.subscribeCamera("NAOqibag", camera, resolution, colorSpace, 5)
    while (camera_enabled):
        pepperImage = camProxy.getImageRemote(videoClient)
        imageWidth = pepperImage[0]
        imageHeight = pepperImage[1]
        array = pepperImage[6]
    
        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), array)
            
        # Save the image.
        image_name = os.path.join(camera_log_dir, 'spqrel_kTopCamera_%f_rgb.png' % time.time())
        im.save(image_name, "PNG")
                
    
        time.sleep(1.0/rate)
        
    camProxy.unsubscribe(videoClient)
    print "Exiting Thread Log Camera "


def rhMonitorThread (memory_service, rate, output_file):
    t = threading.currentThread()
    output_file.write(str(keys_list))
    output_file.write('\n')
    while getattr(t, "do_run", True):
        values =  memory_service.getListData(keys_list)
        ts = time.time()
        timestamp = 'timestamp: %f\n' % ts
        output_file.write(timestamp)
        output_file.write(str(values))        
        output_file.write('\n')

        time.sleep(1.0/rate)
    print "Exiting Thread Log"

def main():
    global camera_enabled
    global current_log_dir
    global camera_frame_rate
    camera_enabled = 0
    camera_frame_rate = 0
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--rate", type=float, default=5,
                        help="Logging rate in Hz")
    parser.add_argument("--keys", type=str, required=True, help="File contaning list of keys to register")
    parser.add_argument("--path", type=str, default=os.getcwd(), help="Path of folder that will contain the logs")
    parser.add_argument("--o", type=str, default="keys.log" ,
                        help="Output file registered values")    
    
    
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    rate = args.rate
    keys_filename = args.keys
    output_filename = args.o
    log_path = args.path

    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        app = qi.Application(["naoqibag", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session
    
    #Starting services
    memory_service  = session.service("ALMemory")

    #Creating logging directory
    log_folder = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    current_log_dir = os.path.join(log_path, log_folder)
    if not os.path.exists(current_log_dir):
        os.makedirs(current_log_dir)

    print "Logging data in: ", current_log_dir
    memory_service.insertData("NAOqibag/CurrentLogFolder", current_log_dir)
    
    #Opening input and output files
    keys_file = open(keys_filename, "r") 
    output_file = open(os.path.join(current_log_dir,output_filename), "w")

    readKeysFile(keys_file, memory_service)
    print keys_list

    
    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,rate,output_file))
    monitorThread.start()

    #subscribe to any change on any touch sensor
    subscriber = memory_service.subscriber("NAOqibag/EnableCamera")
    idEvent = subscriber.signal.connect(functools.partial(onEvent, pip, pport))

    #Program stays at this point until we stop it
    app.run()

    subscriber.signal.disconnect(idEvent)
    monitorThread.do_run = False
    if camera_enabled:
        camera_enabled = 0
        #we give time a cycle of the camera thread to finish
        time.sleep(1/camera_frame_rate)
        
        
    print "Finished"


if __name__ == "__main__":
    main()
