from action_cmd import *

begin()

for i in range(3):
    execPNPaction('turn', '45', interrupt='c1', recovery='waitfor_not_c1; restart_action')
    execPNPaction('say', 'hello')


end()

