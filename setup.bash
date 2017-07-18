_SETUP_DIR=$(builtin cd "`dirname "${BASH_SOURCE[0]}"`" > /dev/null && pwd)

clean_path_var () {
  path_var="$1"
  old_content="$path_var:"; path_var=
  while [ -n "$old_content" ]; do
    x=${old_content%%:*}       # the first remaining entry
    case $path_var: in
      *:"$x":*) ;;         # already there
      *) path_var=$path_var:$x;;    # not there yet
    esac
    old_content=${old_content#*:}
  done
  path_var=${path_var#:}
  unset old_content x
  echo $path_var
}

real_path () {
	python -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$1"
}



if [ "$1" ]; then
	export SPQREL_HOME="$1"
else
	SPQREL_HOME=$_SETUP_DIR
fi

# default home is $HOME/spqrel
export SPQREL_HOME=`real_path "${SPQREL_HOME:-$HOME/spqrel}"`

export LD_LIBRARY_PATH=$SPQREL_HOME/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$SPQREL_HOME/lib:$DYLD_LIBRARY_PATH

# find pnpgen binaries
export PNPGEN_BIN=`find $SPQREL_HOME -path "*/bin/pnpgen_translator"| sed 's@/pnpgen_translator@@'`

export PATH=$SPQREL_HOME/bin:$PATH:$PNPGEN_BIN

export PYTHONPATH=$SPQREL_HOME/spqrel_tools/slu4p:$SPQREL_HOME/worktree/PetriNetPlans/PNPnaoqi/actions:${PYTHONPATH}
export SLU4R_ROOT=$SPQREL_HOME/spqrel_tools/slu4

# Pepper's IP
export PEPPER_IP=localhost

alias shutdown-tmux="tmux list-panes -s -F \"#{pane_pid} #{pane_current_command}\" | grep -v tmux | awk \"{print \\\$1}\" | xargs kill"
alias kill-tmux="tmux list-panes -s -F \"#{pane_pid} #{pane_current_command}\" | grep -v tmux | awk \"{print \\\$1}\" | xargs kill -9"

# clean paths
export LD_LIBRARY_PATH=`clean_path_var $LD_LIBRARY_PATH`
export PATH=`clean_path_var $PATH`
export PYTHONPATH=`clean_path_var $PYTHONPATH`


echo "SPQREL_HOME=$SPQREL_HOME"
echo "PEPPER_IP=$PEPPER_IP"
echo "PATH=$PATH"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH" 
echo "PYTHONPATH=$PYTHONPATH"

export GIT_EXEC_PATH=${SPQREL_HOME}/libexec
