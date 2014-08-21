try:
    import clr
except ImportError:
    raise SystemError('You Must Download pythonnet before and install it !')
import sys
import os
import traceback

__version__ = "3.0"
__test__ = "1.0"
__author__ = "licface@yahoo.com"
__sdk__ = "2.7"
__build__ = "windows"

DLL_PATH = 'c:\Program Files\Simple DNS Plus API for .NET and COM'
if "IronPython" in sys.version:
    clr.AddReferenceToFileAndPath(os.path.join(DLL_PATH, 'SDNSAPI.dll'))
else:
    sys.path.append(DLL_PATH)
    clr.AddReference("SDNSAPI")
#import JHSoftware.SimpleDNSPlus as api
from JHSoftware.SimpleDNSPlus import *

filename = os.path.split(sys.argv[0])[1]
#usage = "\t use : " + filename + " example.com 192.168.10.2 root@example.com"
usage = "\t use : " + filename + " example.com 192.168.10.2 root@example.com ([[host,default=127.0.0.1] [port,default=8053]] [password])"

MASTER_HOST = "192.168.10.2"

def get_host(host):
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

def add(datax,  ip=None):	
    #print "datax =", datax
    host = "127.0.0.1"	
    port = 8053
    passwd = "blackid"

    ipA = "192.168.10.2"
    ipNS = "192.168.10.2"
    ipWWW = "192.168.10.2"
    ipMX = "192.168.10.2"

    #data = tuple(datax)
    data = datax
    #print "data =", data
    add_email = str("root@") + str(get_host(data[0]))

    try:
        if len(datax) > 1:
            try:
                add_host = datax[0]
                add_ip = datax[1]
                ipA = datax[1]
                add_email = datax[2]
                host = datax[3]
                port = datax[4]
                passwd = datax[5]
            except IndexError, e:
                pass

        conn = Connection(host, port, passwd)

        #if sys.argv[1] == None:
        if datax == None or datax == "" or len(datax[0]) == 0:
            print usage
        else:
            #if "www." in sys.argv[1]:
            if "www." in datax[0]:	
                print "\t Sorry !, you can't add zone with preffix \"www.\", please remove \"www.\"\n"
                print usage
            else:
                #data = str(sys.argv[1])
                #if sys.argv[2] == "":
                if ip == "" or ip == None:
                    Zone = conn.CreateZone(data[0], "black-x", str(add_email))
                    #Zone.Records.Add("ftp."+data, "A", ipA)
                    #Zone.Records.Add("ftp."+data, "A", str(sys.argv[2]))
                    Zone.Records.Add("ftp."+ data[0], "A", [str(ipA)])
                    #Zone.Records.Add("mail."+data, "A", ipMX)
                    #Zone.Records.Add("mail."+data, "A", str(sys.argv[2]))
                    Zone.Records.Add("mail."+ data[0], "A", [str(ipA)])
                    Zone.Records.Add("www."+ data[0], "CNAME", [data[0]])
                    #Zone.Records.Add(data, "A", ipA)
                    #Zone.Records.Add(data, "A", str(sys.argv[2]))
                    Zone.Records.Add(data[0], "A", [str(ipA)])
                    #Zone.Records.Add(data, "NS", "black-x")
                    Zone.Records.Add(data[0], "MX", "10", "mail."+ data[0])
                    conn.UpdateZone(Zone, True)
                else:
                    Zone = conn.CreateZone(data[0], "black-x", str(add_email))
                    #Zone.Records.Add("ftp."+data, "A", ipA)
                    #Zone.Records.Add("ftp."+data, "A", str(sys.argv[2]))
                    Zone.Records.Add("ftp."+ data[0], "A", [str(ip)])
                    #Zone.Records.Add("mail."+data, "A", ipMX)
                    #Zone.Records.Add("mail."+data, "A", str(sys.argv[2]))
                    Zone.Records.Add("mail."+ data[0], "A", [str(ip)])
                    Zone.Records.Add("www."+ data[0], "CNAME", [data[0]])
                    #Zone.Records.Add(data, "A", ipA)
                    #Zone.Records.Add(data, "A", str(sys.argv[2]))
                    Zone.Records.Add(data, "A", [str(ip)])
                    #Zone.Records.Add(data, "NS", "black-x")
                    Zone.Records.Add(data, "MX", "10", "mail."+ data[0])
                    conn.UpdateZone(Zone, True)
    except:
        data_e = traceback.format_exc()
        print "ERROR : \n"
        print "\t" + str(data_e)
        print "-"*85
        print "\n"
        print usage
        print "\n"
        print "\t ------------------- script by : licface --------------------"
        
def importfromdb(username, password, host, db, port=None):
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
        
def checkwinhost(name):
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

def importwinhost(name,host='127.0.0.1'):
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
        
def main(datax):
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
