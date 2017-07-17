import qi
import argparse
import sys
import time
import threading
import os

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
            #I was thinking to append only valid keys but will not work if some module is not active yet
            #try:
            #    value =  memory_service.getData(key)
            #    keys_list.append(key)
            #    print "Read key: ", key, value
            #except RuntimeError:
            #    print "Read key: ", key, "Failed"


def rhMonitorThread (memory_service, rate, output_file):
    t = threading.currentThread()
    output_file.write(str(keys_list))
    output_file.write('\n')
    while getattr(t, "do_run", True):
        values =  memory_service.getListData(keys_list)
        timestamp = 'timestamp: %f\n' % time.time()
        output_file.write(timestamp)
        output_file.write(str(values))        
        output_file.write('\n')
        time.sleep(1.0/rate)
    print "Exiting Thread"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--rate", type=int, default=5,
                        help="Logging rate in Hz")
    parser.add_argument("--keys", type=str, required=True, help="File contaning list of keys to register")
    parser.add_argument("--o", type=str, default="out.log" ,
                        help="Output file registered values")    
    
    
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    rate = args.rate
    keys_filename = args.keys
    output_filename = args.o

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

    #Opening input and output files
    keys_file = open(keys_filename, "r") 
    output_file = open(output_filename, "w")

    readKeysFile(keys_file, memory_service)

    print keys_list
    
    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,rate,output_file))
    monitorThread.start()

    #Program stays at this point until we stop it
    app.run()

    monitorThread.do_run = False
    
    print "Finished"


if __name__ == "__main__":
    main()
