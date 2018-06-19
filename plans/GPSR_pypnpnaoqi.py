import os
import sys
import time
import pprint as pp
from support.semantics_interpreter import SemanticResolver

sr = SemanticResolver()

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)


import pnp_cmd_naoqi
from pnp_cmd_naoqi import *


p = PNPCmd()

p.begin()

p.exec_action('setpose', '5.8_10.6_0')

while (not p.get_condition('dooropen')):
    time.sleep(1)

p.exec_action('enter', '30_0_0_4_true')

p.exec_action('navigateto', 'wp5', interrupt='aborted', recovery='restart_action')

#while (not p.get_condition('personhere')):
#    time.sleep(1)

#vsay_starting;
p.exec_action("aimlsay", "greetings")

###
# "The robot can work on at most three commands. After the third command, it has to leave the arena."
###

# "...it has to wait for further commands."
p.exec_action("aimlsay", "requestcommand")
p.exec_action("aimlsay", "speakloud")
# TODO wait

time.sleep(2)

#three runs
for n in range(3):

    #Attemps loop
    repeat_attempts = 0
    understood = False
    while (repeat_attempts < 3 and not understood):
        # This blocks until we get a transcription from google (start language_understanding/google_client.py)
        p.exec_action("googleasr", "gpsr", interrupt="timeout_20")

        # get the google transcription
        googleasr_value = p.memory_service.getData("googleasrresponse")
        print "plan google response", googleasr_value

        if len(googleasr_value) == 0:
            p.exec_action("aimlsay", "misunderstand")
            repeat_attempts = repeat_attempts + 1
        else:
            #We understood something, we ask for confirmation

            # This blocks until we get the task description from the transcription (start language_understanding/language_understanding.py)
            p.exec_action("understandcommand", "gpsr", interrupt="timeout_20")

            # get the interpretation
            commands_inter = eval(p.memory_service.getData("CommandInterpretation"))
            print "plan commands interpretation", pp.pprint(commands_inter)

            #TODO these need to be ordered in order to be executed in order
            for i, task in enumerate(commands_inter):
                print "Task", i, ": ", task["task"]

                print "\tParameters:"
                for req in task["requires"]:
                    if "spotted" in req:
                        for spotreq in req["spotted"]:
                            print "\t"*2, [k for k in req.keys() if k != "spotted"][0] +":", spotreq["text"]

                # repeat command to operator
                try:
                    p.memory_service.insertData("CurrentTaskInterpretation", str(task))
                    p.exec_action("generatetaskdescription", str(i))

                    to_say = str(p.memory_service.getData("task_description"))

                    p.exec_action("say", to_say.replace(" ", "_"))
                except:
                    p.exec_action("say", "I_understood")
                    p.exec_action("say", googleasr_value.replace(" ", "_"))

            p.exec_action("say", "Is_that_correct",interrupt='timeout_5')

            p.exec_action("asr", "confirm")
            try:
                confirm_response = p.memory_service.getData("asrresponse").replace(" ", "_")
            except:
                confirm_response = 'yes'

            if confirm_response != "" and confirm_response == "yes":
                understood = True
            else:
                repeat_attempts = repeat_attempts + 1
                p.exec_action("say", "then_could_you_repeat_the_command_please?",interrupt='timeout_5')


    #we exit the loop either if the correct command or run out of attempts
    if understood:
        p.exec_action("say", "OK_let's_give_it_a_go")
        for i, task in enumerate(commands_inter):
            try:
                res = sr.parse_requires(task["requires"])
                if res['wp'] is not None:
                    p.exec_action("navigateto", res['wp'], interrupt='timeout_120')
                else:
                    p.exec_action("navigateto", res['wp15'], interrupt='timeout_120')
                p.exec_action("say", "sorry_i_have_troubles_to_fully_complete_your_request")
                p.exec_action("navigateto", 'wp5', interrupt='timeout_120')
                break
            except:
                p.exec_action("say", "sorry_i_have_trouble_with_this_right_now")

    else:
        p.exec_action("aimlsay", "nextquestion")


    # understand the command
    #p.exec_action("understandcommand", "")

    #if p.get_condition("commandunderstood"):
    #    p.exec_action("extracttasks", "")

        # repeat the commands understood to the operator
        # and ask when not sure
    #    while not p.get_condition("alltasksconfirmed"):
            # repeat the command to the operator
    #        p.exec_action("generatetaskdescription", "")

    #        p.exec_action("describetask", "")


        #TODO if commands confirmed
    #    p.exec_action("executetasks", "")
        #TODO else ask to repeat

        #GPSRtask; ! *if* timeout_execplan_180 *do* skip_action !
        #p.exec_action("GPSRtask", interrupt="timeout_execplan_180", recovery="skip_action")

        # "..the robot has to move back to the operator to retrieve the next command."
        #navigateto_backdoorin;
        #p.exec_action("navigateto", "backdoorin") # TODO navigate to operator
        #asrenable;
        #p.exec_action("asrenable") # TODO why here?
    #    if n < 2:
    #        p.exec_action("aimlsay", "requestcommand")
    #        time.sleep(2)
    #else:
    #    if n < 2:
    #        p.exec_action("aimlsay", "nextquestion")
    #        time.sleep(2)
        #TODO else i did not understand

     #p.exec_action("aimlsay", "nextquestion")

### exit the arena ###
# "After the third command, it has to leave the arena."
p.exec_action("aimlsay", "farewell")

#recdata_off;
#p.exec_action("rec_data", "off")

p.end()
