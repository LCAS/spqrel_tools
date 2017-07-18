#!/bin/bash

SESSION="${USER}-SPQReL"
SPQREL_PREFIX="${SPQREL_PREFIX:-$HOME/spqrel_launch}"

MAP="$SPQREL_PREFIX/maps/robolabINB1004/robolabINB1004.yaml"

tmux -2 new-session -d -s $SESSION
# Setup a window for tailing log files
#tmux new-window -t $SESSION:0 -n 'pepper core'
tmux new-window -t $SESSION:1 -n 'naoqi-bin'
tmux new-window -t $SESSION:7 -n 'plans'
tmux new-window -t $SESSION:2 -n 'navigation'
tmux new-window -t $SESSION:3 -n 'speech'
#tmux new-window -t $SESSION:4 -n 'objects'
#tmux new-window -t $SESSION:5 -n 'people'
#tmux new-window -t $SESSION:6 -n 'tablet'


tmux select-window -t $SESSION:0
tmux split-window -v
tmux select-pane -t 0
tmux send-keys "ifconfig wlan0" C-m
tmux resize-pane -U 30
tmux select-pane -t 1
tmux send-keys "htop" C-m

# ONLY RUN THIS ON A MACHINE THAT IS NOT A PEPPER (your computer)
tmux select-window -t $SESSION:1
tmux send-keys "# naoqi-bin"

# Navigation Window
tmux select-window -t $SESSION:2
tmux split-window -v
tmux select-pane -t 0
tmux send-keys "cd $SPQREL_PREFIX/bin; ./pepper_localizer --map $MAP --initial_pose_x 0 --initial_pose_y 0 --initial_pose_theta 0" C-m
tmux select-pane -t 1
tmux send-keys "cd $SPQREL_PREFIX/bin; ./pepper_planner --map $MAP " C-m


# Speech Window
tmux select-window -t $SESSION:3
tmux split-window -v
tmux select-pane -t 0
tmux send-keys "cd $SPQREL_PREFIX/slu4p; python speech_to_text/speech_recognition.py -v resources/nuance_grammar.txt -k resources/google_keys.txt" C-m
tmux split-window -h
tmux select-pane -t 1
tmux send-keys "sleep 3;cd $SPQREL_PREFIX/slu4p; python speech_reranking/reranker.py --noun-dictionary resources/noun_dictionary.txt --verb-dictionary resources/verb_dictionary.txt --nuance-grammar resources/nuance_grammar.txt" C-m
tmux select-pane -t 2
tmux send-keys "sleep 6;cd $SPQREL_PREFIX/slu4p; python dialogue_management/dialogue_manager.py -a resources/aiml_kbs/spqrel" C-m
tmux split-window -h
tmux select-pane -t 3
tmux send-keys "sleep 9;cd $SPQREL_PREFIX/slu4p; python text_to_speech/text_to_speech.py" C-m


# Actions and plans 
tmux select-window -t $SESSION:7
tmux split-window -v
tmux select-pane -t 0
tmux send-keys "cd $SPQREL_PREFIX; bin/pnp_naoqi" C-m
tmux split-window -h
tmux select-pane -t 1
tmux send-keys "cd $SPQREL_PREFIX/actions; python init_actions.py" C-m
tmux select-pane -t 2
tmux send-keys "cd $SPQREL_PREFIX/actions" C-m
tmux send-keys "./action_cmd.py -a   -p   -c start"
tmux split-window -h
tmux select-pane -t 3
tmux send-keys "cd $SPQREL_PREFIX/plans" C-m
tmux send-keys "./run_plan.py  "



# Set default window
tmux select-window -t $SESSION:0

# Attach to session
tmux -2 attach-session -t $SESSION

tmux setw -g mode-mouse off

