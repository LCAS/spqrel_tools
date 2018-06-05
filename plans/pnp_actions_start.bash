#!/bin/bash

if [ ${PEPPER_IP:-localhost} == "localhost" ]; then
  echo "Running naoqi..."
  xterm -e "/opt/Aldebaran/naoqi/naoqi-sdk-2.5.5.5-linux64/naoqi " &
  sleep 5
fi

SESSION="${USER}-SPQReL"
SPQREL_PREFIX="${SPQREL_TOOLS:-$HOME/src/SPQReL/qi_ws/spqrel_tools}"

tmux -2 new-session -d -s $SESSION
# Setup a window for tailing log files
tmux new-window -t $SESSION:0 -n 'plans'


# Actions and plans 
tmux select-window -t $SESSION:0
tmux split-window -v
tmux select-pane -t 0
tmux send-keys "pnp_naoqi" C-m
tmux split-window -h
tmux select-pane -t 1
tmux send-keys "cd $SPQREL_PREFIX/actions; python init_actions.py" C-m
tmux select-pane -t 2
tmux send-keys "cd $SPQREL_PREFIX/../PetriNetPlans/PNPnaoqi/py" C-m
tmux send-keys "python pnp_cmd_naoqi.py -a     -p     -c start"
tmux split-window -h
tmux select-pane -t 3
tmux send-keys "cd $SPQREL_PREFIX/plans" C-m
tmux send-keys "./run_plan.py --plan  "



# Set default window
tmux select-window -t $SESSION:0

# Attach to session
tmux -2 attach-session -t $SESSION

tmux setw -g mode-mouse off

