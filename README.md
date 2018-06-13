# spqrel_tools

Development scripts from the SPQReL team.

# Install on PC

* follow instructions in ['INSTALL.md'](./INSTALL.md)
    * you may check out the [`Dockerfile`](https://github.com/LCAS/spqrel_launch/blob/master/Dockerfile) in [`lcas/spqrel_launch`](https://github.com/LCAS/spqrel_launch) for reference of all the steps to set up a system from scratch. This `Dockerfile` is not meant to be taken verbatim, but it documents all general steps required to get a suitable local workspace. Or, simply use the docker image: `docker run --rm -it lcasuol/spqrel_launch` (but only if you understand `docker`).
    * The docker image also provides the perfect, clean cross-compilation environment for pepper. Steps to cross compile in docker, see the [`nut.yml`](https://github.com/LCAS/spqrel_launch/blob/master/nut.yml)

# Working with checked-out code:

1. go to the workspace you want to use (assuming `$HOME/spqrel/workspace`, so `cd $HOME/spqrel/workspace`)
1. clone our top-level repository: `git clone --recurse-submodules https://github.com/LCAS/spqrel_launch.git` (this will pull in all submodules as well
    * the workspace has the following structure (more or less):
        ```
        <ROOT>
          bin/ (where all compiled binaries will end up in)
          lib/ (where all compiled libraries will end up in)
          worktree/
            PetriNetPlans/ (submodule via git clone https://github.com/iocchi/PetriNetPlans.git)
            spqrel_navigation/ (submodule via git clone https://github.com/lcas/spqrel_navigation.git)
            spqrel_tools/ (submodule via git clone https://github.com/lcas/spqrel_tools.git)
        ```
1. go to `cd worktree/spqrel_tools`
1. edit the local config file [`setup-local.bash`](./setup-local.bash) so that cour SDKs are being found and your top-level SPQReL root is being set (_note_: Make sure you don't commit you local changes. run `git update-index --skip-worktree setup-local.bash` once to avoid it being accidentally committed. It's your own configuration that goes in here only.)
1. If you are going to develop in any of the submodules (most likely in `spqrel_tools/`), you will notice that the git head is detached (don't worry if you don't know what I'm talking about). Simply check out the branch you want to work on (usually `git checkout master`) and you are good to go.

# Compile 

1. go to your `spqrel_tools` directory (e.g. `cd $HOME/spqrel/workspace/spqrel_launch/worktree/spqrel_tools`)
1. run `make install` in `spqrel_tools`, it should compile all binaries and translate all plans found, and install everything in the respective places. It will find all qibuild workspaces under `worktree/` (all submodules configured)

_Note: do not `source setup.bash` or `source setup-dev.bash` as they are needed only for running, and somehow get in cmake's way of finding boost._

# Run 

1. make sure you load your local development environment: `source setup-dev.bash` (local computer only) and `source setup.bash` (both local computer and Pepper robot). If you are using tmule (see below, those will be outloaded). 
    * make sure you haven't sourced any other configurations, e.g. ROS workspaces etc. _Never autoload any project-specific environments in your `.bashrc`_.
1. fire up TMule as either:
    * `tmule --config spqrel-local-config.yaml server` (if you want to run locally)
    * `tmule --config spqrel-pepper-config.yaml server` (this is the config usually run on Pepper)

    Either will result in the TMule control server being launched and accessible via web browser wherever it was launched (E.g. on Pepper Wifi address) at port 9999, e.g. http://localhost:9999.
1. Start the TMule sub-systems you want to use (in the browser)
1. In order to make everything is orderly terminated, stop the TMule server with `[Ctrl-C]` and follow this by 
    * `tmule --config spqrel-local-config.yaml terminate` 
    * `tmule --config spqrel-pepper-config.yaml terminate` 

    respectively


# Installation on Pepper:

## Initial git setup (only once):

1. initial SSH setup for git: 
    1. `ssh-keygen -t rsa` if `~/.ssh/id_rsa.pub` doesn't exist yet.
	  1. configure the public key in `~/.ssh/id_rsa.pub` with [github](https://github.com/settings/keys) and [bitbucket](https://bitbucket.org/account/ssh-keys/)
1. create local workspace dir `mkdir -p ~/spqrel` and change into it `cd ~/spqrel`
1. Download snapshot of `pepper` branch of `spqrel_launch` to get initial binaries: `wget https://github.com/LCAS/spqrel_launch/archive/pepper.zip` and unzip it (will give you directory `spqrel_launch-pepper`).
1. `export GIT_EXEC_PATH=$HOME/spqrel/spqrel_launch-pepper/libexec/git-core` to make sure git finds its helpers and set `PATH=$HOME/spqrel/spqrel_launch-pepper/bin:$PATH`
1. still in `~/spqrel` run `git clone --recurse-submodules --depth 1 -b pepper git@github.com:LCAS/spqrel_launch.git` to clone the repository (only shallow clone, we don't need the entire history here)
1. `cd spqrel_launch` and run `update-all.sh` once to make sure everything is updated
1. you may now remove the bootstrap installation  `rm -r ~/spqrel/spqrel_launch-pepper`


## Python installations

1. a hack is needed to get psutil working correctly:
    1. download this psutil zip for binaries for i386: `wget -O /tmp/psutil.zip http://lcas.lincoln.ac.uk/owncloud/index.php/s/p57cSlU8588CdUT/download`
    1. unzip into local python install with `unzip -d ~ /tmp/psutil.zip`
1. `pip install -U --user tmule trollius requests`


## completing installation on Pepper

1. go to `cd ~/spqrel/spqrel_launch/worktree/spqrel_tools`
1. edit `setup-local.bash` with the correct paths
1. `source setup.bash`
1. make sure `setup-local.bash` is not committed: `git update-index --skip-worktree setup-local.bash`
1. configure git:
    1. `git config --global user.email "spqrel@googlegroups.com"`
    1. `git config --global user.name "SPQReL team"`
    1. `git config --global push.default simple`
1. you are ready to go, now let's [Run](#run)

# General Design Considerations about environment setup and making:

* all *general* configurations (applying to both local installation on your computer and on pepper should you into `setup.bash`. This file loads `setup-local.bash` if it exists and must respect the variables defined in `spqrel-local.bash`. They must always take precendence. `setup.bash` is the place to set all required environment variables
* all *development* configurations (e.g. where the find the SDK, etc.) are configured in `setup-dev.bash`. This file also reads `setup-local.bash`, but should only be `source`-d on development machines (i.e. `linux64`) and _not_ on Pepper.
* the `setup-local.bash` contains all the local paths you need to configure for _your_ environment. Changes to that file shall not be committed to the repository ever. Hence, it is good practice to configure it in git to be ignored using `git update-index --skip-worktree setup-local.bash`

