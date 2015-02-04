import Cservice
import pywintypes
import dplay2
import argparse
import sys
import time
import traceback
#import win32serviceutil

def usage():
    print "\n"
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", help="Show Detail Process running", action="store_true")
    parser.add_argument("-c", "--config", help="Set config start Process (auto|demand|disable|delayed-auto)", action="store", type=str)
    parser.add_argument("SERVICE", help="service name", action="store", type=str)
    parser.add_argument("CONF", help="start|stop|restart|status", action="store", type=str)
    #print "len(sys.argv) =", len(sys.argv)
    if len(sys.argv) > 2:
        args =  parser.parse_args()
        if args.SERVICE:
            svc_ctr = Cservice.WService(args.SERVICE)
            if args.CONF:
                if args.CONF == "start":
                    if args.verbosity:
                        print "\t set", svc_ctr.getname()[0], "to start/running ...\n"
                        time.sleep(2)
                    control("start", svc_ctr)
                elif args.CONF == "stop":
                    if args.verbosity:
                        print "\t set", svc_ctr.getname()[0], "to stop ...\n"
                        time.sleep(2)
                    control("stop", svc_ctr)
                elif args.CONF == "restart":
                    if args.verbosity:
                        print "\t set", svc_ctr.getname()[0], "to restart/re-running ...\n"
                        #time.sleep(2)
                    control("restart", svc_ctr)
                    #win32serviceutil.RestartService(args.SERVICE)
                    control("status", svc_ctr)
                elif args.CONF == "status":
                    if args.verbosity:
                        print "\t get service status of", svc_ctr.getname()[0], " ...\n"
                        time.sleep(2)
                    control("status", svc_ctr)
                else:
                    parser.print_help()
            else:
                parser.print_help()
        else:
            print "\n"
            print "\t Please insert name of SERVIVE !\n"
            print parser.print_help()

        if args.config:
            if args.verbosity:
                print "\t set", svc_ctr.getname()[0], "to start with", args.config, "\n"
                time.sleep(2)
            setstart(args.config)
    else:
        parser.print_help()

def control(status, svc_ctr):
    if status == "start":
        svc_ctr.start()
    elif status == "stop":
        svc_ctr.stop()
    elif status == "restart":
        svc_ctr.restart()
    elif status == "status":
        print "\t Service", svc_ctr.getname()[0], "is", svc_ctr.status()

def setstart(start):
    svc_ctr.setstartup(start)

if __name__ == "__main__":
    try:
        usage()
    except:
        traceback.format_exc_syslog_growl()