This folder contains actions for plans to be executed with pnp_naoqi

== Setup ==

$ export PYTHONPATH=$PYTHONPATH:<PATH_TO>/PetriNetPlans/PNPpepper/actions

Example:

$ export PYTHONPATH=$PYTHONPATH:$HOME/src/PetriNetPlans/PNPpepper/actions


== Convention for actions ==

(see examples in this folder)

* Starting all the actions:

Run init_actions.py


== Convention for conditions ==

Condition <phi> is implemented with the AL key "PNP_cond_"+<phi> 
whose value can be 0/1 or false/true


Setting condition example:

  $ cd pepper_tools/memory
  $ ./write.py --key PNP_cond_dooropen --val 1



