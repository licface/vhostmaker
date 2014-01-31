import os
import Cservice
from iniparse import INIConfig
from iniparse import ConfigParser

import Cservice

cfg = INIConfig(file(os.path.join(os.path.dirname(__file__),"conf.ini")))
cfg2 = ConfigParser()
cfg2.read('conf.ini')
print "cfg2.get('SERVER','SERVERSVC') =",cfg2.get('SERVER','SERVERSVC')
#print "cfg2.SERVER.SERVERSVC =",cfg2.SERVER.SERVERSVC
cfg2.set('SERVER','SERVERSVC','TESTSETSET')
#cfg.SERVER.SERVERSVC = "TEST"
print "cfg2.get('SERVER','SERVERSVC') =",cfg2.get('SERVER','SERVERSVC')