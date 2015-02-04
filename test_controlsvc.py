import Cservice
import time
import sys

def controlSvc(svcname, state):
    srvname = Cservice.WService(svcname)
    if str(state).lower() == 'restart':
        while True:
            srvname.stop()
            if srvname.status() == "RUNNING":
                print "service running"
                time.sleep(2)
            else:
                srvname.start()
                
if  __name__ == '__main__':
    controlSvc(sys.argv[1], sys.argv[2])
                