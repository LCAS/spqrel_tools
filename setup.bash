export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/spqrel/lib
export PATH=$PATH:$HOME/spqrel/bin

export PYTHONPATH=${PYTHONPATH}:/home/nao/spqrel/slu4p

export PEPPER_IP=localhost

alias shutdown-tmux="tmux list-panes -s -F \"#{pane_pid} #{pane_current_command}\" | grep -v tmux | awk \"{print \\\$1}\" | xargs kill"
alias kill-tmux="tmux list-panes -s -F \"#{pane_pid} #{pane_current_command}\" | grep -v tmux | awk \"{print \\\$1}\" | xargs kill -9"
