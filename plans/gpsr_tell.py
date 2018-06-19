from support.semantics_interpreter import SemanticResolver

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *
import logging
from pprint import pformat

logging.basicConfig(level='INFO')

class GPSR_tell:

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

    def say(self, text=''):
        self.a('say', text.replace(' ', '_'))

    def execute(self, text_to_say, entity=None):
        # logging.info(pformat(sr.entities))
        if entity is not None:
            wp = self.sr.resolve_wp(entity)
            if wp is not None:
                self.a('taskstep', 'going there')
                self.a('navigateto', wp)
        while self.p.get_condition('personhere') and not self.sim:
            self.a('turn', '45')
        self.say(text_to_say)


def main():
    p = PNPCmd()

    p.begin()
    plan = GPSR_tell(p, sim=False)
    plan.execute()

    p.end()

if __name__ == '__main__':
    main()
