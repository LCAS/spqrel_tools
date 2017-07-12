_SETUP_DIR=$(builtin cd "`dirname "${BASH_SOURCE[0]}"`" > /dev/null && pwd)

if [ "$1" ]; then
	export SPQREL_HOME="$1"
else
	SPQREL_HOME=$_SETUP_DIR
fi

# default home is $HOME/spqrel
export SPQREL_HOME=`readlink -f "${SPQREL_HOME:-$HOME/spqrel}"`

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SPQREL_HOME/lib
export PATH=$PATH:$SPQREL_HOME/bin

export PYTHONPATH=$SPQREL_HOME/spqrel_tools/slu4p:$SPQREL_HOME/PetriNetPlans/PNPnaoqi/actions:${PYTHONPATH}
export SLU4R_ROOT=$SPQREL_HOME/spqrel_tools/slu4

# Pepper's IP
export PEPPER_IP=localhost

alias shutdown-tmux="tmux list-panes -s -F \"#{pane_pid} #{pane_current_command}\" | grep -v tmux | awk \"{print \\\$1}\" | xargs kill"
alias kill-tmux="tmux list-panes -s -F \"#{pane_pid} #{pane_current_command}\" | grep -v tmux | awk \"{print \\\$1}\" | xargs kill -9"

# find all python dirs:

echo "SPQREL_HOME=$SPQREL_HOME"
echo "PEPPER_IP=$PEPPER_IP"
#echo "PATH=$PATH"| tr ":" "\n\t"
#echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH" | tr ":" "\n\t"
#echo "PYTHONPATH=$PYTHONPATH"| tr ":" "\n\t"


