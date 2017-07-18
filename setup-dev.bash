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

export PYNAOQI=`find "${SPQREL_HOME}" -path "*/pynao*/lib/python2.7/site-packages" | tr "\n" ":"`
export PYTHONPATH=${PYNAOQI}:$PYTHONPATH

export NAOQI_LIB=`find "${SPQREL_HOME}" -path "*/naoqi*/lib/libqi.*" | sed 's/libqi.*$//' |  tr "\n" ":"`
export LD_LIBRARY_PATH=${NAOQI_LIB}:${LD_LIBRARY_PATH}
export DYLD_LIBRARY_PATH=${NAOQI_LIB}:${DYLD_LIBRARY_PATH}

export NAOQI_BIN=`find "${SPQREL_HOME}" -path "*/naoqi*/bin/naoqi-bin" | sed 's/naoqi-bin//'  | tr "\n" ":"`
export PATH=${NAOQI_BIN}:${PATH}



PYTHONPATH=`clean_path_var $PYTHONPATH`
LD_LIBRARY_PATH=`clean_path_var $LD_LIBRARY_PATH`
PATH=`clean_path_var $PATH`

echo "found pynaoqi in $PYNAOQI"
echo "found SDK in $NAOQI_LIB"
