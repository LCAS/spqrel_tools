#!/bin/bash
SESSION=$USER

tmux -2 new-session -d -s $SESSION

# window 0
tmux rename-window 'Robot'
tmux split-window -h
tmux select-pane -t 0
tmux send-keys "cd /home/nao/pepper_tools/cmd_server" C-m
tmux send-keys "python websocket_pepper.py" C-m
sleep 3
tmux select-pane -t 1

# Set default window
tmux select-window -t $SESSION:0

# Attach to session
#tmux -2 attach-session -t $SESSION

