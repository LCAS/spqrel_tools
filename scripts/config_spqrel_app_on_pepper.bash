#!/bin/bash

PEPPER_SPQREL_DIR=${HOME}/spqrel

# create app folder
cd ~/.local/share/PackageManager/apps/
mkdir -p spqrel/html/
cd spqrel/html/
# create home page with logo
echo "<html><body><br><br><br><center><img src=\"img/logo.gif\" width=800></center></body></html>" > index.html
mkdir img
cd img
cp ${PEPPER_SPQREL_DIR}/spqrel_launch/worktree/spqrel_tools/html/img/logo.gif .
# setting links to spqrel html app 
cd ${PEPPER_SPQREL_DIR}
ln -s ~/.local/share/PackageManager/apps/spqrel/html/ html
cd html
ln -s ${PEPPER_SPQREL_DIR}/spqrel_launch/worktree/spqrel_tools/modim_actions robocup2018



