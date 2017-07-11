.PHONY: all plans

PLANS:=$(shell find plans -name "*.plan")

PNMLS=$(PLANS:.plan=.pnml)

PNPTRANS:=../../PetriNetPlans/PNPgen/bin/pnpgen_translator
INSTALL_TREE:=../../install
WORKTREE:=..
QIBUILDS:=$(shell find $(WORKTREE) -name qiproject.xml)


all:	$(PNMLS) build

plans:	$(PNMLS)
	@echo $^

plans/%.pnml: plans/%.plan
	cd plans/; $(PNPTRANS) inline $*.plan > $*-trans.logs

install: $(PNMLS) build
	rsync -a $(WORKTREE) $(INSTALL_TREE)

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