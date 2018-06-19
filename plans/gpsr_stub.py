from support.semantics_interpreter import SemanticResolver

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *
import logging
from pprint import pformat

logging.basicConfig(level='INFO')

class GPSR:

    def __init__(self, p, sim=False):
        self.p = p
        self.sim = sim
        self.sr = SemanticResolver()

    def a(self, action, param='', interrupt='', recovery=''):
        if self.sim:
            logging.info("SIMULATE ACTION: %s(%s)" % (action, param))
        else:
            try:
                return self.p.exec_action(action, param, interrupt, recovery)
            except Exception as e:
                logging.error(
                    'action %s with param %s failed to be started in plan: %s' %
                    (action, param, str(e)))

    def execute(self):
        # logging.info(pformat(sr.entities))
        from gpsr_tell import GPSR_tell
        tell = GPSR_tell(self.p, self.sim)
        tell.execute('this is for you', 'kitchen')
        self.a('taskstep', 'done')


def main():
    p = PNPCmd()

    p.begin()
    plan = GPSR(p, sim=True)
    plan.execute()

    p.end()

if __name__ == '__main__':
    main()
