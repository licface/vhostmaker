try:
    import clr
except ImportError:
    raise SystemError('You Must Download pythonnet before and install it !')
import sys
import os
import traceback
import argparse
#import JHSoftware.SimpleDNSPlus as api
DLL_PATH = 'c:\Program Files\Simple DNS Plus API for .NET and COM'
if "IronPython" in sys.version:
    clr.AddReferenceToFileAndPath(os.path.join(DLL_PATH, 'SDNSAPI.dll'))
else:
    sys.path.append(DLL_PATH)
    clr.AddReference("SDNSAPI")
from JHSoftware.SimpleDNSPlus import *
import sendgrow
import System

__version__ = "3.1"
__test__ = "1.0"
__author__ = "licface@yahoo.com"
__sdk__ = "2.7"
__build__ = "windows"

class simplednshostadd:

    def __init__(self, host, passwd, port=8053, ipA=None, ipNS=None, ipWWW=None, ipMX=None, ipMail=None, ipFtp=None, ipAll=None, email=None):
        
        self.filename = os.path.split(sys.argv[0])[1]
        #usage = "\t use : " + filename + " example.com 192.168.10.2 root@example.com"
        self.use = "\t use : " + self.filename + " example.com 192.168.10.2 root@example.com ([[host,default=127.0.0.1] [port,default=8053]] [password])"
        self.conn = Connection(host, port, passwd)
        if ipAll == None:
            self.host = host
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

    def add_Zone(self, datax=None):
        if datax == None or datax == "" or len(datax[0]) == 0:
            print usage(True)
        else:
            try:
                if "www." in datax[0]:	
                    print "\t Sorry !, you can't add zone with preffix \"www.\", please remove \"www.\"\n"
                    print usage
                else:
                    #(hostname, ipFtp, ipMail, ipWWW, ipA, ipMX, remote_host, remote_port, remote_password, email)
                    #print "datax 1 =", datax
                    Zone = self.conn.CreateZone(datax[0], str(datax[4]), str(datax[-1]))
                    #print "datax[1] =", datax[1]
                    Zone.Records.Add("ftp."+ datax[0], "A", [str(datax[1])])
                    Zone.Records.Add("mail."+ datax[0], "A", [str(datax[2])])
                    Zone.Records.Add("www."+ datax[0], "CNAME", [datax[3]])
                    Zone.Records.Add(datax[0], "A", [str(datax[4])])
                    Zone.Records.Add(datax[0], "MX", "10", "mail."+ datax[4])
                    self.conn.UpdateZone(Zone, True)
            except System.Net.WebException:
                print "\n"
                print "\t Can't Connect to DNS Server(SimpleDNS Server) !"
                os._exit(1)
                return False
            

    def add(self, hostname, remote_port=8053, ipA=None, ipNS=None, ipWWW=None, ipMX=None, ipFtp=None, ipMail=None, remote_host=None, password=None, email=None, datax=None, verbosity=None):
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
        if email == None:
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
                data_tmp.append(ipFtp)
                data_tmp.append(ipMail)
                data_tmp.append(ipWWW)
                data_tmp.append(ipA)
                data_tmp.append(ipMX)
                data_tmp.append(remote_host)
                data_tmp.append(remote_port)
                data_tmp.append(password)
                data_tmp.append(add_email)
                #print 'data_tmp =', data_tmp
                self.add_Zone(data_tmp)

        except:
            data_e = traceback.format_exc()
            self.sendnotify(str(data_e), msg="Error: ")
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
                #if len(datax) > 1:
                    #data = []
                    #for i in range(1, len(sys.argv)):
                    #    data.append(sys.argv[i])
                    #   add(datax)
                    #importwinhost(sys.argv[1])
                #else:
                    #data = sys.argv[1]
                #    add(data)
                    #importwinhost(sys.argv[1])

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
        parser.add_argument('HOST', help='host name to add', action='store')
        parser.add_argument('-A', '--ipA', help='ip address A default: ' + self.host, action='store')
        parser.add_argument('-NS', '--ipNS', help='ip address NS default: ' + self.host, action='store')
        parser.add_argument('-WWW', '--ipWWW', help='ip address WWW default: ' + self.host, action='store')
        parser.add_argument('-MX', '--ipMX', help='ip address MX default: ' + self.host, action='store')
        parser.add_argument('-FTP', '--ipFTP', help='ip address FTP default: ' + self.host, action='store')
        parser.add_argument('-MAIL', '--ipMAIL', help='ip address MAIL defalt: ' + self.host, action='store')
        parser.add_argument('-e', '--email', help='email host server', action='store')
        parser.add_argument('-H', '--host', help='ip/hostname SimpleDNS Server', action='store')
        parser.add_argument('-P', '--password', help='password access to SimpleDNS Server', action='store')
        parser.add_argument('-p', '--port', help='port SimpleDNS Server, default=8053', action='store')
        parser.add_argument('-d', '--datax', help='list of argv data', action='store')
        parser.add_argument('-v', '--verbosity', help='print running process', action='store_true')
        if len(sys.argv) < 2:
            parser.print_help()
        elif printhelp:
            parser.print_help()
        else:
            args = parser.parse_args()
            try:
                if args.HOST:
                    #(self, hostname, remote_port=8053, ipA=None, ipNS=None, ipWWW=None, ipMX=None, ipFtp=None, ipMail=None, remote_host=None, password=None, email=None, datax=None)
                    self.add(args.HOST, args.port, args.ipA, args.ipNS, args.ipWWW, args.ipMX, args.ipFTP, args.ipMAIL, args.host, args.password, args.email, args.datax, args.verbosity)
            except parser.error:
                parser.print_help()
                
def main(hostname):
    mc = simplednshostadd('192.168.10.2', 'blackid')
    #mc.usage()
    mc.add(hostname)
        
#if __name__ == '__main__':
    
    #main()
