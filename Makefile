.PHONY: all plans build install configure install_prep

PLANS:=$(shell find plans -name "*.plan")

PNMLS=$(PLANS:.plan=.pnml)

PNPTRANS?=../../PetriNetPlans/PNPgen/bin/pnpgen_translator
INSTALL_TREE?=../../install
WORKTREE?=..
QIBUILDS:=$(shell find $(WORKTREE) -name qiproject.xml)


all:	$(PNMLS) build

clean: 
	rm -rf $(PNMLS)
	for qb in $(QIBUILDS); do \
		d=`dirname $$qb`; \
		(cd $$d; pwd; qibuild clean -f) \
	done
	rm -rf $(INSTALL_TREE)
	rm -rf cookies

plans:	$(PNMLS)
	@echo $^

plans/%.pnml: plans/%.plan
	cd plans/; $(PNPTRANS) inline $*.plan > $*-trans.log

$(INSTALL_TREE)/.git:
	mkdir -p $(INSTALL_TREE)
	git clone --depth 1 https://github.com/lcas/spqrel_launch.git $(INSTALL_TREE)

install_prep: $(INSTALL_TREE)/.git

install: $(PNMLS) build install_prep
	rsync -a --exclude '.git' --exclude '.gitignore' $(WORKTREE) $(INSTALL_TREE)
	(cd $(INSTALL_TREE); git add -A && git commit --allow-empty -a -m "$$USER-`date`")

build:	$(QIBUILDS) cookies/configure
	for qb in $(QIBUILDS); do \
		d=`dirname $$qb`; \
		(cd $$d; pwd; qibuild make) \
	done

cookies/configure:	$(QIBUILDS)
	for qb in $(QIBUILDS); do \
		d=`dirname $$qb`; \
		(cd $$d; pwd; qibuild configure) \
	done
	mkdir -p cookies; touch $@

configure: cookies/configure