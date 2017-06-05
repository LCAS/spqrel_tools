import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "waitfor"


def actionThread_exec (params):
	t = threading.currentThread()
	memory_service = getattr(t, "mem_serv", None)
	print "Action "+actionName+" started with params "+params
	# action init
	val = False
	# action init
	while (getattr(t, "do_run", True) and (not val)): 
		print "Action "+actionName+" "+params+" exec..."
		# action exec
		try:
			cval = get_condition(memory_service, params)
			val = (cval.lower()=='true') or (cval=='1')
		except:
			pass
		# action exec
		time.sleep(0.25)
		
	print "Action "+actionName+" "+params+" terminated"
	# action end

	# action end
	memory_service.raiseEvent("PNP_action_result_"+actionName,"success");



if __name__ == "__main__":
    main(actionName, actionThread_exec)

