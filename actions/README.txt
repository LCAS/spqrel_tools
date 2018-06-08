This folder contains actions for plans to be executed with pnp_naoqi

== Setup ==

$ export PYTHONPATH=$PYTHONPATH:<PATH_TO>/PetriNetPlans/PNPnaoqi/actions

Example:

$ export PYTHONPATH=$PYTHONPATH:$HOME/src/PetriNetPlans/PNPnaoqi/actions


== Actions ==

(see examples in this folder)

* Starting all the action servers:

    Run init_actions.py

* Test a single action

    $ cd $PNP_HOME/PNPnaoqi/py/
    $ ./pnp_cmd_naoqi.py -a <actionname> -p <params> -c <start|end|interrupt>


== Conditions ==

Condition <phi> is implemented with the AL key "PNP_cond_"+<phi>
whose value can be 0/1 or false/true

* Command line

Setting condition:

    $ cd $PNP_HOME/PNPnaoqi/actions
    $ ./set_condition.py -c <condition> -v <true|false>

Getting condition:

    $ cd $PNP_HOME/PNPnaoqi/actions
    $ ./get_condition.py -c <condition>


* Python script


    import conditions

    memory_service  = app.session.service("ALMemory")

    cond = 'condition'
    val = 'true'
    conditions.set_condition(memory_service,cond,val)
    conditions.get_condition(memory_service,cond)




===========================================================================

SPQReL actions/conditions implemented

SPQReL actions

aimlsay.py          generates a sentence to be spoken using AIML  param: <pattern> the pattern to be matched in the aiml kbs 
asrenable.py        enables ASR (off to disable)     param: [on|off]  default:on
assign.py           assign a value to a key     params: <key>_<value>
continuebtn.py 		continuebtn_show shows the continue button, continuebtn_hide hide it
dialogue.py         executes a dialogue blocking     param: name of dialogue
dialoguestart.py    starts a dialogue non-blocking   param: name of dialogue
dialoguestop.py     stops a previously started dialogue
enter.py            NOT USED
execplan.py         reads LU4R string, generates and executes the plan
followuntil.py      acivates follow until a condition param: termination condition
goto.py             goto a position label   param: position label
headpose.py         moves the head          param: yaw, pitch [degrees]
lookfor.py          continuously move the head left and right until condition   param: termination condition
memorizeface.py     ???
memorizepeople.py   ???
navigateto.py      ???
posture.py          sets the posture    param: Stand, Crouch, WakeUp, Rest
recdata.py          enable/disable data recording     param: on|off
saveposition.py     saves the current position of the robot - param: name given to the position
say.py              say with ALTextToSpeech    param: label of what to say
soundtrack.py       moves the body towards the sound detected
speechbtn.py        ???
trackface.py        coninuouly tracks the face of the person in front with the head - param: termination condition
turn.py             turns the robot     params: <angle_DEG>_[<REL|ABS>] REL default
vsay.py             say with Andrea tool    param: label of what to say
waitfor.py          waits until condition   param: termination condition
wait.py             waits n seconds         param: seconds to wait
webpage.py          (NOT USED) displays a web page


SPQReL conditions implemented

dooropen.py         true if laser detects free space in front
movementdetected.py true when a continous movement (around 3-4 sec) is detected
obstaclehere.py     true if laser detects obstance in front
personbehind.py     true when person something is behind the robot within a distance of 0.9m
persondetected.py   true when People list is bigger than 1
personhere.py       true when a person is in front of the robot within a distance of 1.5m
personsitting.py    true when a person is found sittin (threshold now at 1.4m heigh)
screentouched.py    true if screen is touched
