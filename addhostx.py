try:
    import clr
except ImportError:
    raise SystemError('You Must Download pythonnet before and install it !')
import sys
import os
import traceback
import argparse
import ConfigParser
from clr import System
DLL_PATH = ''
cfg = ConfigParser.RawConfigParser()
fileconfig = os.path.join(os.path.dirname(__file__), 'conf.ini')
if os.path.isfile(fileconfig):
    cfg.read(fileconfig)
    if os.path.isdir(cfg.get('SDNSAPI', 'DLL_PATH')):
        DLL_PATH = cfg.get('SDNSAPI', 'DLL_PATH')
    else:
        DLL_PATH = ''
else:
    if DLL_PATH == '':
        DLL_PATH_1 = 'c:\Program Files (x86)\Simple DNS Plus API for .NET and COM'
        DLL_PATH_2 = 'c:\Program Files\Simple DNS Plus API for .NET and COM'
        if os.path.isdir(DLL_PATH_1):
            DLL_PATH = DLL_PATH_1
        elif os.path.isdir(DLL_PATH_2):
            DLL_PATH = DLL_PATH_2
        else:
            raise SystemError('SDNSAPI and/or DLL NOT FOUND')

if "IronPython" in sys.version:
    clr.AddReferenceToFileAndPath(os.path.join(DLL_PATH, 'SDNSAPI.dll'))
else:
    sys.path.append(DLL_PATH)
    clr.AddReference("SDNSAPI")
from JHSoftware.SimpleDNSPlus import *
import sendgrowl

__version__ = "3.2"
__test__ = "1.0"
__author__ = "licface@yahoo.com"
__sdk__ = "2.7"
__build__ = "windows"

class simplednshostadd:

    def __init__(self, remotehost='127.0.0.1', passwd=None, port=8053, ipA=None, ipNS=None, ipWWW=None, ipMX=None, ipMail=None, ipFtp=None, ipAll=None, email=None, host=None, verbosity=None):
        
        self.filename = os.path.split(sys.argv[0])[1]
        self.verbosity = verbosity
        self.remotehost = remotehost
        #usage = "\t use : " + filename + " example.com 192.168.10.2 root@example.com"
        self.use = "\t use : " + self.filename + " example.com 192.168.10.2 root@example.com ([[host,default=127.0.0.1] [port,default=8053]] [password])"
        # print "MAIN HOST =", host
        # print "MAIN PORT =", port
        # print "MAIN PASSWD =", passwd
        self.conn = ''
        if remotehost != None and passwd != None:
            self.conn = Connection(remotehost, int(port), passwd)
        if ipAll == None:
            self.remotehost = remotehost
            self.port = int(port)
            self.passwd = passwd
    
            self.ipA = ipA
            self.ipNS = ipNS
            self.ipWWW = ipWWW
            self.ipMX = ipMX
            self.ipMail = ipMail
            self.ipFtp = ipFtp
            self.email = email
        else:
            self.host = ipAll
            self.port = int(port)
            self.passwd = ipAll
    
            self.ipA = ipAll
            self.ipNS = ipAll
            self.ipWWW = ipAll
            self.ipMX = ipAll
            self.ipMail = ipAll
            self.ipFtp = ipAll
            if email == None:
                self.email = ''
            else:
                self.email = email
        # print "ipAll =", ipAll
        # print "self.host =", self.host
        
    def sendnotify(self, message, title="SimpleDNSPlus - Control Add Host", msg=""):
        mclass = sendgrow.growl()
        icon = os.path.join(os.path.dirname(__file__), 'simpledns.png')
        event = 'SimpleDNS Plus - AddHost'
        text =  msg + "\"" + str(message) +  "\""
        appname = 'SimpleDNSPlus'
        mclass.publish(appname, event, title, text, iconpath=icon)    

    def get_host(self, host):
        d3 = ''
        if 'www.' in host:
            d1 = str(host).split('www.') #['www', 'xxx.com']
            return d1[-1]
        elif 'http://' in host:
            if 'www.' in host:
                d1 = str(host).split('http://www.') #['www', 'xxx.com']            
                return d1[-1]
            else:
                d1 = str(host).split('http://') #['www', 'xxx.com']            
                return d1[-1]
        else:
            return host

    def del_zone(self, hostname, remotehost=None, port=None, passwd=None):  
        if remotehost != None:
            self.remotehost = remotehost
        if port != None:
            self.port = int(port)
        if passwd != None:
            self.passwd = passwd
        try:  
            if self.conn == '':
                self.conn = Connection(self.remotehost, int(self.port), self.passwd)
            self.conn.RemoveZone(str(hostname))
        except System.Net.WebException:
            print "\tHostname is Not FOUND or Please set Host and Password SimpleDNS Server"
            self.usage(True)

    def add_Zone(self, datax=None):
        if datax == None or datax == "" or len(datax[0]) == 0:
            print usage(True)
        else:
            if "www." in datax[0]:  
                print "\t Sorry !, you can't add zone with preffix \"www.\", please remove \"www.\"\n"
                print usage
            else:
                # print "datax 001 =", datax
                if datax[-2] == None:
                    print "Remote server password NOT FOUND !"
                    sys.exit(0)
                # print "datax[0] =", datax[0]
                #(hostname, ipFtp, ipMail, ipWWW, ipA, ipMX, remote_host, remote_port, remote_password, email)
                if datax[-1] == '' or datax[-1] == 'root@':
                    datax[-1] = 'root@' + datax[0]
                # print "datax 1 =", datax
                if self.conn == '':
                    self.conn = Connection(datax[6], int(datax[7]), datax[8])
                Zone = self.conn.CreateZone(datax[0], str(datax[4]), str(datax[-1]))
                # print "datax =", datax
                Zone.Records.Add("ftp."+ datax[0], "A", [str(datax[1])])
                Zone.Records.Add("mail."+ datax[0], "A", [str(datax[2])])
                Zone.Records.Add("www."+ datax[0], "CNAME", [datax[0]])
                Zone.Records.Add(datax[0], "A", [str(datax[4])])
                Zone.Records.Add(datax[0], "MX", "10", "mail."+ datax[0])
                # print 'self.conn =', self.conn
                self.conn.UpdateZone(Zone, True)    

    def updateZone(self, ip, host=None):
        if self.conn == '':
            self.conn = Connection(self.remotehost, int(self.port), self.passwd)

        if host == None:
            zlist = self.conn.GetZoneList(0)
            for i in zlist:
                host = i.ZoneName
                Zone = self.conn.CreateZone(host, ip, 'root@'+str(host))
                Zone.Records.Add("ftp." + str(host), "A", [ip])
                Zone.Records.Add("mail." + host, "A", [ip])
                Zone.Records.Add("www." + host, "CNAME", [host])
                Zone.Records.Add(host, "A", [ip])
                Zone.Records.Add(host, "MX", "10", "mail." + host)
                self.conn.UpdateZone(Zone, True)
        else:
            Zone = self.conn.CreateZone(host, ip, 'root@'+str(host))
            Zone.Records.Add("ftp." + str(host), "A", [ip])
            Zone.Records.Add("mail." + host, "A", [ip])
            Zone.Records.Add("www." + host, "CNAME", [host])
            Zone.Records.Add(host, "A", [ip])
            Zone.Records.Add(host, "MX", "10", "mail." + host)
            self.conn.UpdateZone(Zone, True)

    def add(self, hostname, remote_port=8053, ipA=None, ipNS=None, ipWWW=None, ipMX=None, ipFtp=None, ipMail=None, remote_host='127.0.0.1', password=None, email=None, datax=None, verbosity=None, ipAll =None):
        if ipAll != None:
            ipA = ipAll
            ipNS = ipAll
            ipWWW = ipAll
            ipMX = ipAll
            ipFtp =ipAll
            ipMail = ipAll

        data_to = []
        if ipA == None:
            if self.ipA == None:
                ipA = self.host
            else:
                ipA = self.ipA
        if ipNS == None:
            if self.ipNS == None:
                ipNS = self.host
            else:
                ipNS = self.ipNS
        if ipWWW == None:
            if self.ipWWW == None:
                ipWWW = self.host
            else:
                ipWWW = self.ipWWW
        if ipMX == None:
            if self.ipMX == None:
                ipMX = self.host
            else:
                ipMX = self.ipMX
        if ipMail == None:
            if self.ipMail == None:
                ipMail = self.host
            else:
                ipMail = self.ipMail
        if ipFtp == None:
            if self.ipFtp == None:
                ipFtp = self.host
            else:
                ipFtp == self.ipFtp
        if email == None or email == '':
            add_email = str("root@") + str(self.get_host(hostname))
        else:
            add_email = str(email)
        try:
            if isinstance(datax, list):
                if len(datax) == 10:
                    try:
                        self.add_Zone(datax)
                    except IndexError, e:
                        pass
                elif len(datax) == 4:
                    datax_temp1 = datax[0]
                    datax_temp2 = datax[1:]
                    datax = []
                    datax.append(datax_temp1)
                    datax.append(ipFtp)
                    datax.append(ipMail)
                    datax.append(ipWWW)
                    datax.append(ipA)
                    datax.append(ipMX)
                    if remote_host == None or password == None:
                        raise SyntaxError('Please Definiton Remote Host and Password')
                    else:
                        datax.append(remote_host)
                        datax.append(remote_port)
                        datax.append(password)
                else:
                    print "Please re-configurate your datax, length datax is %s" % (str(len(datax)))
                    print "if datax is used"
                    if self.ipA == None or self.ipA == '':
                        self.usage(True)
                        raise SystemError('Please definition what configuration use will use')
            else:
                data_tmp = []
                data_tmp.append(hostname)
                # print "host =", hostname
                data_tmp.append(ipFtp)
                # print "ipFtp =", ipFtp
                data_tmp.append(ipMail)
                # print "ipMail =", ipMail
                data_tmp.append(ipWWW)
                # print "ipWWW =", ipWWW
                data_tmp.append(ipA)
                # print "ipA =", ipA
                data_tmp.append(ipMX)
                # print "ipMX =", ipMX
                data_tmp.append(remote_host)
                # print "remote_host =", remote_host
                data_tmp.append(remote_port)
                # print "remote_port =", remote_port
                data_tmp.append(password)
                # print "password =", password
                data_tmp.append(add_email)
                # print "add_email =", add_email
                # print "remote_host =", remote_host
                # print 'data_tmp =', data_tmp
                self.add_Zone(data_tmp)

        except:
            data_e = traceback.format_exc()
            self.sendnotify(str(data_e), msg="Error: ")
            if verbosity:
                print "ERROR : \n"
                print "\t" + str(data_e)
                print "-"*85
                print "\n"
            self.usage(True)
            print "\n"
            print "\t ------------------- script by : licface --------------------"

    def importfromdb(self, username, password, host, db, port=None):
        try:
            db = MySQLdb.connect(host,username,password,db)
            cursor = db.cursor()

            sql = "SELECT * FROM " + str(db)
            cursor.execute(sql)
            #db.commit()
            results = cursor.fetchall()
            for row in results:
                print row

        except IndexError, e:
            os.system('cls')
            data_e = traceback.format_exc()
            #print "ERROR : \n"
            #print "\t" + str(data_e)
            #print "-"*85
            print "\n"
            print usage
            print "\n"
            print "\t ------------------- script by : licface --------------------"

        except MySQLdb.DatabaseError, e:
            if "Duplicate" in e[1]:
                print "\n"
                print "\t Vhost has been added ! \n"
            else:
                pass

    def checkwinhost(self, name):
        f = open("c:\Windows\System32\drivers\etc\hosts", "r")
        g = f.readlines()
        for i in g:
            if name in i:
                f.close()
                return False
            else:
                pass
        f.close()
        return True

    def importwinhost(self, name, host='127.0.0.1'):
        if checkwinhost(name) == True:
            f = open("c:\Windows\System32\drivers\etc\hosts", "a")
            if "http://" in name:
                if "www." in name:
                    name = str(name).split("www.")[1]
                else:
                    name = str(name).split("http://")[1]
            if MASTER_HOST == None or MASTER_HOST == '':
                f.write(name,host)
            else:
                f.write("\n" + MASTER_HOST + "    " + name)
            f.close()
        else:
            print "\n"
            print "\t HOST \"", name, "\"has been inserted on Windows Host File ! \n"

    def main(self, datax):
        try:
            if datax == "import":
                importfromdb("root","blackid","localhost","site")
            else:
                add(datax)
        except:
            data_e = traceback.format_exc()
            #if sys.argv[-1] == "-v":
            print "ERROR : \n"
            print "\t" + str(data_e)
            print "-"*85
            print "\n"
            #print usage

    def usage(self, printhelp=None):
        #print "len(sys.argv) =", len(sys.argv)
        print "\n"
        usage = "HOST [options]"
        parser = argparse.ArgumentParser(usage=usage)
        parser.add_argument('HOST', help='host name to add or type "update" for Update IP(-U)', action='store')
        parser.add_argument('-A', '--ipA', help='ip address A', action='store')
        parser.add_argument('-NS', '--ipNS', help='ip address NS', action='store')
        parser.add_argument('-WWW', '--ipWWW', help='ip address WWW', action='store')
        parser.add_argument('-MX', '--ipMX', help='ip address MX', action='store')
        parser.add_argument('-FTP', '--ipFTP', help='ip address FTP', action='store')
        parser.add_argument('-MAIL', '--ipMAIL', help='ip address MAIL', action='store')
        parser.add_argument('-e', '--email', help='email host server', action='store')
        parser.add_argument('-H', '--host', help='ip/hostname SimpleDNS Server', default='127.0.0.1', action='store')
        parser.add_argument('-P', '--password', help='password access to SimpleDNS Server', default='blackid', action='store')
        parser.add_argument('-p', '--port', help='port SimpleDNS Server, default=8053', default=8053, type=int, action='store')
        parser.add_argument('-d', '--datax', help='list of argv data', action='store')
        parser.add_argument('-v', '--verbosity', help='print running process', action='store_true')
        parser.add_argument('-a', '--all', help='IP for All', action='store')
        parser.add_argument('-U', '--update', help='Update/Replace All Host IP, type "update" on HOST option ', action="store", dest='ipaddress')
        parser.add_argument('-r', '--remove', help='Remove hostname', action='store_true')
        if len(sys.argv) < 2:
            parser.print_help()
        elif printhelp:
            parser.print_help()
        else:
            args = parser.parse_args()
            self.__init__(args.host, args.password, args.port, args.ipA, args.ipNS, args.ipWWW, args.ipMX, args.ipMAIL, args.ipFTP, args.all, args.email, args.HOST, args.verbosity)
            # print "args =", args
            self.verbosity = args.verbosity
            try:
                if args.HOST:
                    #(self, hostname, remote_port=8053, ipA=None, ipNS=None, ipWWW=None, ipMX=None, ipFtp=None, ipMail=None, remote_host=None, password=None, email=None, datax=None)
                    if args.remove:
                        self.del_zone(args.HOST)
                    if args.all:
                        # add(self, hostname, remote_port=8053, ipA=None, ipNS=None, ipWWW=None, ipMX=None, ipFtp=None, ipMail=None, remote_host='127.0.0.1', password=None, email=None, datax=None, verbosity=None, ipAll =None):
                        self.add(args.HOST, args.port, args.all, args.all, args.all, args.all, args.all, args.all, args.host, args.password, args.email, args.datax, args.verbosity, args.all)
                    else:
                        if args.remove:
                            pass
                        else:
                            if args.HOST == str('update').lower():
                                if args.ipaddress:
                                    self.__init__(args.host, args.password, args.port, args.ipA, args.ipNS, args.ipWWW, args.ipMX, args.ipMAIL, args.ipFTP, args.all, args.email, args.HOST)
                                    self.updateZone(args.ipaddress)        
                            else:
                                self.add(args.host, args.port, args.ipA, args.ipNS, args.ipWWW, args.ipMX, args.ipFTP, args.ipMAIL, args.host, args.password, args.email, args.datax, args.verbosity, args.all)
                
            except parser.error:
                if args.verbosity:
                    print " ERROR:", traceback.format_exc()
                parser.print_help()
                
def main(ipAll, hostname=None, password=None):
    mc = simplednshostadd(host=hostname, ipAll=ipAll)
    # mc.usage()
    if hostname == None:
        mc.usage()
    else:
        mc.add(hostname=hostname, ipAll=ipAll, password=password)
        
if __name__ == '__main__':
    
    mc = simplednshostadd()
    mc.usage()
