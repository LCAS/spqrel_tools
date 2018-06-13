#!/usr/bin/env bash
_SETUP_DIR=$(builtin cd "`dirname "${BASH_SOURCE[0]}"`" > /dev/null && pwd)

ENVFILE="`mktemp -p /tmp env.XXXX`"
env | sort > "$ENVFILE"

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

if [ -r "$_SETUP_DIR/setup-local.bash" ]; then
  source "$_SETUP_DIR/setup-local.bash"
fi

if [ "$1" ]; then
	export SPQREL_HOME="$1"
else
  if [ -z "$SPQREL_HOME" ]; then
	  export SPQREL_HOME=$_SETUP_DIR
  else
    export SPQREL_HOME
  fi
fi

# default home is $HOME/spqrel
export SPQREL_HOME=`real_path "${SPQREL_HOME}"`
export SPQREL_CONFIG="$SPQREL_HOME/worktree/spqrel_tools/scripts/spqrel-config.yaml"
export SPQREL_TOOLS="$SPQREL_HOME/worktree/spqrel_tools"
export PNP_HOME="$SPQREL_HOME/worktree/PetriNetPlans"

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SPQREL_HOME/lib

# find pnpgen binaries
export PNPGEN_BIN=`find $SPQREL_HOME -path "*/bin/pnpgen_translator"| sed 's@/pnpgen_translator@@'`

export PATH=$PATH:$SPQREL_HOME/bin:$PNPGEN_BIN

export PYTHONPATH="${PYTHONPATH}:$SPQREL_TOOLS/slu4p:$SPQREL_HOME/worktree/PetriNetPlans/PNPnaoqi/actions:$SPQREL_HOME/worktree/PetriNetPlans/pyPNP:$SPQREL_TOOLS/scripts:$SPQREL_HOME/worktree/spqrel_navigation/src/topological_navigation/scripts/"

export SLU4R_ROOT="$SPQREL_TOOLS/slu4p"
export PLAN_DIR="$SPQREL_TOOLS/plans"

# meaningfull default which may already have been set in setup-local.bash

export PEPPER_IP="${PEPPER_IP:-localhost}"
export MAP="${MAP:-$SPQREL_HOME/maps/nagoya/dummy.yaml}"
export TMAP="${TMAP:-$SPQREL_HOME/maps/nagoya/dummy.tpg}"
export LU4R_IP="${LU4R_IP:-192.168.127.16}"

export MODIM_HOME="$SPQREL_HOME/worktree/modim"
export PEPPER_TOOLS_HOME="$SPQREL_HOME/worktree/pepper_tools"

# clean paths
export LD_LIBRARY_PATH=`clean_path_var $LD_LIBRARY_PATH`
export PATH=`clean_path_var $PATH`
export PYTHONPATH=`clean_path_var $PYTHONPATH`





# echo "  SPQREL_HOME=$SPQREL_HOME" >& 2
# echo "  SPQREL_TOOLS=$SPQREL_TOOLS" >& 2
# echo "  SLU4R_ROOT=$SLU4R_ROOT" >& 2
# echo "  PEPPER_IP=$PEPPER_IP" >& 2
# echo "  PATH=$PATH" >& 2
# echo "  MODIM_HOME=$MODIM_HOME" >& 2
# echo "  PEPPER_TOOLS_HOME=$PEPPER_TOOLS_HOME" >& 2
# echo "  LD_LIBRARY_PATH=$LD_LIBRARY_PATH"  >& 2
# echo "  PYTHONPATH=$PYTHONPATH" >& 2

if [ -d ${SPQREL_HOME}/libexec/git-core ]; then
    export GIT_EXEC_PATH=${SPQREL_HOME}/libexec/git-core
fi

# display environment changes if we are running interactively.
if [ "$PS1" -a `uname -n` != "Pepper" ] ; then
    echo "configured ENV changes:"
    env | sort| diff --unchanged-line-format= --old-line-format= --new-line-format='%L' "$ENVFILE" -  | sed 's/^/  /'
fi
rm "$ENVFILE"
