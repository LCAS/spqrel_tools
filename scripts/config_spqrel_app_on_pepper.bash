#!/bin/bash

PEPPER_SPQREL_DIR=${HOME}/spqrel

cd ~/.local/share/PackageManager/apps/
mkdir -p spqrel/html/
cd spqrel/html/
echo "<html><body><h1>Ciao</h1></body></html>" > index.html
cd ${PEPPER_SPQREL_DIR}
ln -s ~/.local/share/PackageManager/apps/spqrel/html/ html
cd html
ln -s ${PEPPER_SPQREL_DIR}/spqrel_launch/worktree/spqrel_tools/modim_actions robocup2018

