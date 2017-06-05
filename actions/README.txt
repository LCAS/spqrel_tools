This folder contains actions for plans to be executed with pnp_naoqi

Set-up

$ export PYTHONPATH=$PYTHONPATH:<PATH_TO>/PetriNetPlans/PNPpepper/actions

Example:

$ export PYTHONPATH=$PYTHONPATH:$HOME/src/PetriNetPlans/PNPpepper/actions


Convention for actions:

(see examples in PetriNetPlans/PNPpepper/actions and in this folder)


Convention for conditions:

Condition <phi> is implemented with the AL key "PNP_cond_"+<phi> whose value can be
0,1 or false/true



