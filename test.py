import conf
import os
import Cservice
from iniparse import INIConfig

cfg = INIConfig(file(os.path.join(os.path.dirname(__file__),"conf.ini")))
print "cfg.PATH.MASTER =",cfg.PATH.MASTER
if os.path.isdir(cfg.PATH.MASTER):
    print "cfg.PATH.MASTER =",cfg.PATH.MASTER
    print True
else:
    print "cfg.PATH.MASTER =",cfg.PATH.MASTER
    print False
        
    
    
