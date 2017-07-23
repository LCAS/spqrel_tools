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

asrenable.py        enables ASR,         param 'off' to disable
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
movementdetected.py ???
navigate_to.py      ???
obstaclehere.py     condition: true if laser detects obstance in front
personbehind.py     ???
persondetected.py   ???
personhere.py       ???
personsitting.py    ???
posture.py          sets the posture    param: Stand, Crouch, WakeUp, Rest
saveposition.py     ???
say.py              say with ALTextToSpeech    param: label of what to say
screentouched.py    condition: true if screen is touched
soundtrack.py       ???
speechbtn.py        ???
trackface.py        ???
turn.py             turns the robot     params: <angle_DEG>_<REL|ABS>
vsay.py             say with Andrea tool    param: label of what to say
waitfor.py          waits until condition   param: termination condition
wait.py             waits n seconds         param: seconds to wait
webpage.py          (NOT USED) displays a web page



