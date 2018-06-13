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


export NAOQI_HOME=${NAOQI_HOME:-/opt/naoqi}

export SPQREL_HOME=`real_path "${SPQREL_HOME}"`

export PYNAOQI=`find "${NAOQI_HOME}" -path "*/pynao*/lib/python2.7/site-packages" | tr "\n" ":"`
export PYTHONPATH=${PYNAOQI}:$PYTHONPATH

export NAOQI_LIB=`find "${NAOQI_HOME}" -path "*/naoqi*/lib/libqi.*" | sed 's/libqi.*$//' |  tr "\n" ":"`
export LD_LIBRARY_PATH="${NAOQI_LIB}:${LD_LIBRARY_PATH}"
export DYLD_LIBRARY_PATH=${NAOQI_LIB}:${DYLD_LIBRARY_PATH}

export NAOQI_BIN=`find "${NAOQI_HOME}" -path "*/naoqi*/bin/naoqi-bin" | sed 's/naoqi-bin//'  | tr "\n" ":"`
export PATH="${NAOQI_BIN}:${PATH}"



PYTHONPATH=`clean_path_var $PYTHONPATH`
LD_LIBRARY_PATH=`clean_path_var $LD_LIBRARY_PATH`
DYLD_LIBRARY_PATH=`clean_path_var $DYLD_LIBRARY_PATH`
PATH=`clean_path_var $PATH`

if [ -z "$PYNAOQI" ]; then
  echo "couldn't find pynaoqi"  >& 2
fi

if [ -z "$NAOQI_LIB" ]; then
  echo "couldn't find C++ SDK"  >& 2
fi

# display environment changes if we are running interactively.
if [ "$PS1" ]; then
    echo "configured ENV changes:"
    env | sort| diff --unchanged-line-format= --old-line-format= --new-line-format='%L' "$ENVFILE" -  | sed 's/^/  /'
fi

rm "$ENVFILE"
