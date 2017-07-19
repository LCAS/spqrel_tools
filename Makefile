.PHONY: all plans build install configure install_prep

PLANS:=$(shell find plans -name "*.plan")

PNMLS=$(PLANS:.plan=.pnml)

# set you toolchain according to your qibuild toolchains, default is cross-compilatio for pepper,
# usually, we should have only "pepper" and "linux64", as described at https://sites.google.com/a/dis.uniroma1.it/peppino/software-setup
TOOLCHAIN?=linux64

AUX_DIRS=scripts actions plans maps setup.bash

# worktree, usually one level up
WORKTREE?=$(shell readlink -f ..)

# path to the pnp_translator
PNPTRANS=$(WORKTREE)/PetriNetPlans/PNPgen/bin/pnpgen_translator

# install tree for the full installation
INSTALL_TREE?=$(shell readlink -f ../..)

# find git repos:
GIT_REPOS:=$(shell find  ${WORKTREE} -maxdepth 2 -name .git  | sed 's/.git//' | xargs -n 1 -r readlink -f)

GIT_BRANCH=$(TOOLCHAIN)

QIBUILDS:=$(shell find $(WORKTREE) -name qiproject.xml)
QIBUILDS_DIRS=$(QIBUILDS:/qiproject.xml=)
QIBUILDS_BUILD_DIRS=$(QIBUILDS_DIRS:=/build-$(TOOLCHAIN))

QI_CONF_OPTS:=-w $(WORKTREE) -c $(TOOLCHAIN) --release
QI_MAKE_OPTS:=-c $(TOOLCHAIN) 

all:	 build

update:
	for d in ${GIT_REPOS}; do \
		(cd $$d; git pull); \
	done

clean: cookies/configure-$(TOOLCHAIN)
	rm -rf $(PNMLS)
	for qb in $(QIBUILDS); do \
		d=`dirname $$qb`; \
		(cd $$d; pwd; qibuild clean -z -s -f) \
	done
	rm -rf cookies

BINS:=$(shell find $(QIBUILDS_BUILD_DIRS) -type f  | xargs -r file | grep "LSB executable" | cut -f1 -d: | grep -v CMakeFiles)
LIBS:=$(shell find $(QIBUILDS_BUILD_DIRS) -type f -a -name "*.so" | xargs -r file | grep "LSB shared object" | cut -f1 -d: | grep -v CMakeFiles)

bins: build $(BINS) $(LIBS)
	@echo $(QIBUILDS_BUILD_DIRS)
	@echo $(BINS)
	@echo $(LIBS)

pnp_trans: $(WORKTREE)/PetriNetPlans/PNPgen/bin/pnpgen_translator

$(PNPTRANS):
	-(cd $(WORKTREE)/PetriNetPlans/PNP/include && ln -s /usr/include/FlexLexer.h .)
	(cd $(WORKTREE)/PetriNetPlans/PNP && mkdir -p build && \
		cd build && cmake .. && make)
	(cd $(WORKTREE)/PetriNetPlans/PNPgen && mkdir -p build && \
		cd build && cmake .. && make)

install_bins: bins
	install -d $(INSTALL_TREE)/bin $(INSTALL_TREE)/lib
	install $(BINS) $(INSTALL_TREE)/bin
	install -m 664 $(LIBS) $(INSTALL_TREE)/lib

plans:	$(PNMLS)
	@echo $^

plans/%.pnml: plans/%.plan $(PNPTRANS)
	cd plans/; $(PNPTRANS) inline $*.plan > $*-trans.log

# $(INSTALL_TREE)/.git:
# 	mkdir -p $(INSTALL_TREE)
# 	(git clone --depth 1 --recursive -b $(GIT_BRANCH) \
# 			--single-branch https://github.com/lcas/spqrel_launch.git $(INSTALL_TREE) || \
# 	 git init $(INSTALL_TREE))
	 

# install_prep: $(INSTALL_TREE)/.git

# install_pull: #install_prep
# 	(cd $(INSTALL_TREE); \
# 		git pull && git checkout $(TOOLCHAIN))

install: $(PNMLS)  install_bins
#	rsync -a --exclude '.git' --exclude '.gitignore' $(WORKTREE)/* $(INSTALL_TREE)
#	rsync -a --exclude '.git' --exclude '.gitignore' $(AUX_DIRS) $(INSTALL_TREE)
	# (cd $(INSTALL_TREE); \
	# 	git add -A --ignore-removal bin lib && \
	# 	git commit --allow-empty -a -m "committed by $$USER from `hostname` at `date`")

# push: install
# 	(cd $(INSTALL_TREE); \
# 		git push)

build:	$(QIBUILDS) cookies/configure-$(TOOLCHAIN)
	for qb in $(QIBUILDS); do \
		d=`dirname $$qb`; \
		(cd $$d; pwd; qibuild make $(QI_MAKE_OPTS)) \
	done

$(WORKTREE)/.qi:
	cd $(WORKTREE); qibuild init; qibuild add-config pepper -t pepper; qibuild add-config linux64 -t linux64

cookies/configure-$(TOOLCHAIN):	$(QIBUILDS) $(WORKTREE)/.qi $(PNPTRANS)
	for qb in $(QIBUILDS); do \
		d=`dirname $$qb`; \
		(cd $$d; pwd; qibuild configure $(QI_CONF_OPTS)) \
	done
	mkdir -p cookies; touch $@

configure: cookies/configure-$(TOOLCHAIN)

reconfigure: 
	-rm cookies/configure-$(TOOLCHAIN)
	$(MAKE) configure
