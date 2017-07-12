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

if [ "$1" ]; then
	export SPQREL_HOME="$1"
else
	SPQREL_HOME=$_SETUP_DIR
fi

# default home is $HOME/spqrel
export SPQREL_HOME=`readlink -f "${SPQREL_HOME:-$HOME/spqrel}"`

export PYNAOQI=`find "${SPQREL_HOME}" -path "*/pynao*/lib/python2.7/site-packages" | xargs -r -n 1 -- readlink -f | tr "\n" ":"`

export PYTHONPATH=${PYNAOQI}:$PYTHONPATH

PYTHONPATH=`clean_path_var $PYTHONPATH`

echo "found pynaoqi in $PYNAOQI"