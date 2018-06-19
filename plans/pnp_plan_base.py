from support.semantics_interpreter import SemanticResolver

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *
from pprint import pformat
import logging

logging.basicConfig(level='WARNING')


class PlanBase(object):

    def __init__(self, p=None, sim=False):
        self.logger = logging.getLogger('PlanBase')
        if p is None:
            self.p = PNPCmd()
        else:
            self.p = p
        self.sim = sim
        if sim:
            self.logger.setLevel('INFO')
        self.sr = SemanticResolver()

    def cond(self, cond, default=True):
        if self.sim:
            self.logger.info("     COND: %s(%s)" % (cond, default))
            return default
        else:
            return self.p.get_condition(cond)

    def set_cond(self, cond, value="true"):
        if self.sim:
            self.logger.info("      SET: %s(%s)" % (cond, value))
            return value
        else:
            return self.p.set_condition(cond, value)

    def unset_cond(self, cond):
        if self.sim:
            self.logger.info("    UNSET: %s(%s)" % (cond, 'false'))
            return value
        else:
            return self.p.set_condition(cond, "false")

    def a(self, action, param='', interrupt='', recovery=''):
        if self.sim:
            self.logger.info("   ACTION: %s(%s)" % (action, param))
        else:
            try:
                return self.p.exec_action(action, param, interrupt, recovery)
            except Exception as e:
                self.logger.error(
                    'action %s with param %s failed to be started in plan %s' %
                    (action, param, str(e)))


class TestPlan(PlanBase):

    def __init__(self, p, sim=True):
        PlanBase.__init__(self, p, sim)

    def execute(self):
        # self.logger.info(pformat(sr.entities))
        self.cond('sdf')
        self.set_cond('sdf')
        self.a('taskstep', 'done')
        self.a('taskstep', 'next')
        self.a('taskstep', 'final')


def main():
    p = PNPCmd()

    p.begin()
    plan = TestPlan(p, sim=True)
    plan.execute()

    p.end()


if __name__ == '__main__':
    main()
