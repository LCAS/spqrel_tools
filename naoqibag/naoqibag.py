import qi
import argparse
import sys
import time
import threading
import os
import functools

from naoqi import ALProxy
import Image

# Bag format
# 0: SPQReL
# 1: CSV typed
bag_format = 1

# data read from files
keys_list = []
shortnames_list = []
types_list = []

def readKeysFile(keys_file, memory_service):
    global keys_list, shortnames_list, types_list
    for line in keys_file:
        key = line.strip()
        if len(key) == 0 or key[0] == '#':
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
            v = key.split(',')
            keys_list.append(v[0])
            n = v[0].strip()
            if (len(v)>1):
                n = v[1].strip()
            shortnames_list.append(n)
            t = 'double'
            if (len(v)>2):
                t = v[2].strip()
            types_list.append(t)

def onEventCamera(pip, pport, value):
    global camera_enabled
    global camera_frame_rate
    print "value: ", value 
    if (float(value)==0):
        camera_enabled = 0
    else:
        camera_enabled = 1
        camera_frame_rate = float(value)
        #create a thead that monitors directly the signal
        camMonitorThread = threading.Thread(target = cameraMonitorThread, args = (pip, pport, camera_frame_rate))
        camMonitorThread.start()        

def manageRecord(memory_service, rate, output_file, value):
    global keylogThread
    global keylog_enabled
    print "value: ", value 
    
    if (value):
        keylog_enabled = True
        #create a thead that monitors directly the signal
        keylogThread = threading.Thread(target = rhMonitorThread, args = (memory_service,rate,output_file))
        keylogThread.start()
    else:
        keylog_enabled = False
        keylogThread.do_run = False

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
    fps = rate
    cameraname = "NAOqibag"+str(time.time())
    videoClient = camProxy.subscribeCamera(cameraname, camera, resolution, colorSpace, int(fps))
    #camProxy.setFrameRate(videoClient, int(fps))
    print "Current camera rate: ", camProxy.getFrameRate(videoClient)
    while (camera_enabled):
        pepperImage = camProxy.getImageRemote(videoClient)
        if (pepperImage != None):
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
    print 'Recording data at @%.2f Hz ...' %rate

    t = threading.currentThread()
    logheader(output_file,keys_list)
    while getattr(t, "do_run", True):
        try:
            values = memory_service.getListData(keys_list)
            if logdata(output_file,values):
                sys.stdout.write('.') # full log ok
            else:
                sys.stdout.write('-') # missing values
        except Exception as e:
            sys.stdout.write('X') # error
            print e


        sys.stdout.flush()
        time.sleep(1.0/rate)
    print "Exiting Thread Log"


# TTS callback
#Event: "ALTextToSpeech/CurrentSentence"
#callback(std::string eventName, std::string value, std::string subscriberIdentifier)

def TTSCurrentSentenceCB(value):
    print "TTSCurrentSentenceCB: ",value


# Touch screen signal 

# qi::Signal<float, float> ALTabletService::onTouchDown
def touchscreenCB(x, y):
    print "touchscreenCB: ", x, " ", y



def logheader(output_file,keys_list):
    global bag_format
    if bag_format==0:  # SPQReL
        output_file.write(str(keys_list))
        output_file.write('\n')
    elif bag_format==1:  # CSV typed
        # names
        output_file.write('timestamp')
        output_file.write(',')
        for n in shortnames_list[0:len(shortnames_list)-1]:            
            output_file.write(n)
            output_file.write(',')
        output_file.write(shortnames_list[len(shortnames_list)-1])
        output_file.write('\n')
        # types
        output_file.write('double') # timestamp
        output_file.write(',')
        for t in types_list[0:len(types_list)-1]:
            output_file.write(t)
            output_file.write(',')
        output_file.write(types_list[len(types_list)-1])
        output_file.write('\n')


def checkValue(v):
    if (v!=None):
        return str(v)
    else:
        return '0'

def logdata(output_file,values):
    global bag_format
    r = True # return true if not missing values
    ts = time.time()
    if bag_format==0:  # SPQReL
        timestamp = 'timestamp: %f\n' % ts
        output_file.write(timestamp)
        output_file.write(str(values))
        output_file.write('\n')
    elif bag_format==1:  # CSV typed
        output_file.write(str(ts))
        output_file.write(',')
        for v in values[0:len(values)-1]:
            if (v==None):
                r = False
            s = checkValue(v)
            output_file.write(s)
            output_file.write(',')
        v = values[len(values)-1]
        if (v==None):
            r = False
        s = checkValue(v)
        output_file.write(s)
        output_file.write('\n')
    return r

def main():
    global camera_enabled
    global current_log_dir
    global camera_frame_rate
    global keylogThread
    global keylog_enabled

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
    parser.add_argument("--pause", type=bool, default=False, help="Pause the start of the logging")
    parser.add_argument("--o", type=str, default="keys.log" ,
                        help="Output file registered values")    
    
    
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    rate = args.rate
    keys_filename = args.keys
    output_filename = args.o
    log_path = args.path
    pause = args.pause

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
    try:
        tablet_service  = session.service("ALTabletService")
    except:
        tablet_service  = None
        print 'Cannot open ALTabletService'
    

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

    
    #subscribe to event to enable log recording
    subscriber_record = memory_service.subscriber("NAOqibag/Rec")
    idEvent_record = subscriber_record.signal.connect(functools.partial(manageRecord, memory_service, rate, output_file))
    if pause:
        keylog_enabled = False
    else:
        #start recording 
        manageRecord(memory_service, rate, output_file, 1)
        keylog_enabled = True

    #subscribe to event to enable camera recording
    subscriber_camera = memory_service.subscriber("NAOqibag/EnableCamera")
    idEvent_camera = subscriber_camera.signal.connect(functools.partial(onEventCamera, pip, pport))

    if (tablet_service!=None):
        # Touch screen listener
        sigTTS = tablet_service.onTouchDown.connect(callback)


    eventTTS = 'ALTextToSpeech/CurrentSentence'
    subTTS = memory_service.subscriber(eventTTS)
    idEventTTS = subTTS.signal.connect(TTSCurrentSentenceCB)


    #Program stays at this point until we stop it
    app.run()


    # Closing all event listeners
    subscriber_camera.signal.disconnect(idEvent_camera)
    subTTS.signal.disconnect(idEventTTS)

    if (tablet_service!=None):
        tablet_service.onTouchDown.disconnect(sigTTS)
    
    if keylog_enabled:
        keylogThread.do_run = False

    if camera_enabled:
        camera_enabled = 0
        #we give time a cycle of the camera thread to finish
        time.sleep(1/camera_frame_rate)
    
    subscriber_record.signal.disconnect(idEvent_record)
        
    print "Finished"


if __name__ == "__main__":
    main()
