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



