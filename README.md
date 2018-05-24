# spqrel_tools
Development scripts from the spqrel team

# Install on PC

* check out the [`Dockerfile`](https://github.com/LCAS/spqrel_launch/blob/master/Dockerfile) in [`lcas/spqrel_launch`](https://github.com/LCAS/spqrel_launch) to get working overall steps to set up a system from scratch. This `Dockerfile` is not meant to be taken verbatim, but it documents all general steps required to get a suitable local workspace.

Or, simply use the docker image: `docker run -it lcasuol/spqrel_launch`.
* The docker image also provides the perfect, clean cross-compilation environment for pepper. Steps to cross compile in docker, see the [`nut.yml`](https://github.com/LCAS/spqrel_launch/blob/master/nut.yml)
* install tmule: `sudo pip install -U tmule` 


# Compile and Start

* run `make` in `spqrel_tools`, it should compile all binaries and translate all plans found
* got to the `spqrel_tools` directory
* configure your local environment in `setup-local.bash` (e.g. like [this](https://github.com/LCAS/spqrel_tools/blob/master/setup-local.bash)), in particular, set the path to all the NAOQI SDKs and the path to the top-level SPQReL directory structure, i.e. to `spqrel_launch`.
* fire up TMule as either:
  * `tmule --config spqrel-local-config.yaml server` (if you want to run locally)
  * `tmule --config spqrel-pepper-config.yaml server` (this is the config usually run on Pepper)

  Either will result in the TMule control server being launched and accessible via web browser wherever it was launched (E.g. on Pepper Wifi address).
* Start the TMule sub-systems you want to use
* In order to make everything is orderly terminated, stop the TMule server with `[Ctrl-C]` and follow this by 
  * `tmule --config spqrel-local-config.yaml terminate` 
  * `tmule --config spqrel-pepper-config.yaml terminate` 

  respectively


