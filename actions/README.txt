This folder contains actions for plans to be executed with pnp_naoqi

== Setup ==

$ export PYTHONPATH=$PYTHONPATH:<PATH_TO>/PetriNetPlans/PNPnaoqi/actions

Example:

$ export PYTHONPATH=$PYTHONPATH:$HOME/src/PetriNetPlans/PNPnaoqi/actions


== Actions ==

(see examples in this folder)

* Starting all the actions:

    Run init_actions.py

* Test a single action

    $ cd actions
    $ ./action_cmd -a <actionname> -p <params> -c <start|end|interrupt>


== Conditions ==

Condition <phi> is implemented with the AL key "PNP_cond_"+<phi> 
whose value can be 0/1 or false/true


Setting condition example:

  $ cd pepper_tools/memory
  $ ./write.py --key PNP_cond_dooropen --val 1



===========================================================================

SPQReL actions implemented

asrenable.py        enables ASR (off to disable)     param: [on|off]  default:on
dialogue.py         executes a dialogue blocking     param: name of dialogue
dialoguestart.py    starts a dialogue non-blocking   param: name of dialogue
dialoguestop.py     stops a previously started dialogue
dooropen.py         condition: true if laser detects free space in front
enter.py            NOT USED
execplan.py         reads LU4R string, generates and executes the plan
followuntil.py      acivates follow until a condition param: termination condition
goto.py             goto a position label   param: position label
headpose.py         moves the head          param: yaw, pitch [degrees]
lookfor.py          continuously move the head left and right until condition   param: termination condition
memorizeface.py     ???
memorizepeople.py   ???
movementdetected.py condition: true when a continous movement (around 3-4 sec) is detected 
navigate_to.py      ???
obstaclehere.py     condition: true if laser detects obstance in front
personbehind.py     condition: true when person something is behind the robot within a distance of 0.9m
persondetected.py   condition: true when People list is bigger than 1 
personhere.py       condition: true when a person is in front of the robot within a distance of 1.5m
personsitting.py    condition: true when a person is found sittin (threshold now at 1.4m heigh)
posture.py          sets the posture    param: Stand, Crouch, WakeUp, Rest
saveposition.py     saves the current position of the robot - param: name given to the position
say.py              say with ALTextToSpeech    param: label of what to say
screentouched.py    condition: true if screen is touched
soundtrack.py       moves the body towards the sound detected
speechbtn.py        ???
trackface.py        coninuouly tracks the face of the person in front with the head - param: termination condition
turn.py             turns the robot     params: <angle_DEG>_[<REL|ABS>] REL default
vsay.py             say with Andrea tool    param: label of what to say
waitfor.py          waits until condition   param: termination condition
wait.py             waits n seconds         param: seconds to wait
webpage.py          (NOT USED) displays a web page



