import os
import sys
import re
#import argparse
import optparse
import string
import Cservice
import ConfigParser
import subprocess
import addhostx as addhost
import sendgrowl

__author__ = "licface@yahoo.com"
__version__ = "1.5"
__test__ = "0.1"
__sdk__ = "2.7"
__build__ =  "windows"
__platform_test__ = 'nt'
__changelog__ = 'remove argparse and change with optparse with quiet support'

class maker:
    def __init__(self, host=None,path=None,email=None):
        self.host = host
        self.path = path
        self.email = email     
        self.masterpath = None
        self.FILECONF = os.path.join(os.path.dirname(__file__),"conf.ini")
        self.cfg = ConfigParser.RawConfigParser()
        #self.cfg.add_section('PATH')
        self.cfg.read(self.FILECONF)
        self.cfgsave = ConfigParser.SafeConfigParser()
        self.cfgsave.read(self.FILECONF)
        
    def get_key(self, bits, pem, C, ST, L, O, OU, CN, emailaddr, output_password='', challengePassword=''):
        """
            get inserted key for SSL key config return variabel key string
        
        [req]
            default_bits           = 
            default_keyfile        = .pem
            distinguished_name     = 
            attributes             = 
            prompt                 = 
            output_password        = 
        
        [req_distinguished_name]
            C                      = 
            ST                     = 
            L                      = 
            O                      = 
            OU                     = 
            CN                     = 
            emailAddress           = 
        
        [req_attributes]
            challengePassword      = 
        """        
        key = """
[req]
default_bits           = %d
default_keyfile        = %s.pem
distinguished_name     = req_distinguished_name
attributes             = req_attributes
prompt                 = no
output_password        = %s

[req_distinguished_name]
C                      = %s
ST                     = %s
L                      = %s
O                      = %s
OU                     = %s
CN                     = %s
emailAddress           = %s

[req_attributes]
challengePassword      = %s
        """ % (bits, pem, output_password, C, ST, L, O, OU, CN, emailaddr, challengePassword)
        return key

    def make_key_config(self, bits, pem, OU, CN, emailaddr, C='XX', ST='WestLand', L='NeveLand', O='LICFACE', output_password='', challengePassword=''):
        """
        make_key_config(self, bits, pem, OU, CN, emailaddr, C='XX', ST='WestLand', L='NeveLand', O='LICFACE', output_password='', challengePassword='')
        
        data = self.get_key(bits, pem, C, ST, L, O, OU, CN, emailaddr, output_password, challengePassword)
        
            path = os.path.join(os.getenv('TEMP'), CN + "_temp.key")
            f = open(path, "w")
            f.write(data)
            f.close()
            return path
        """
        data = self.get_key(bits, pem, C, ST, L, O, OU, CN, emailaddr, output_password, challengePassword)
        path = os.path.join(os.getenv('TEMP'), CN + "_temp.key")
        f = open(path, "w")
        f.write(data)
        f.close()
        return path

    def writeconf(self,section,option,value):
        """
        write config by section, option and value
            >> writeconf(self,section,option,value)
		"""
        self.cfgsave.set(section,option,value)
        with open(self.FILECONF, 'w') as configfile:
            self.cfgsave.write(configfile)

    def get_OU(self, host):
        d3 = ''
        if 'www.' in host:
            d1 = str(host).split('www') #['www', 'xxx.com']
            if len(d1) > 1:
                if "." in d1[1]:
                    d2 = str(d1[1]).split(".") #['xxx', 'com']
                    if len(d2[-1]) == 2 or len(d2[-1]) == 3:
                        for i in range(0, len(d2) - 1):
                            d3 = d3 + d2[i]
                    else:
                        for i in range(0, len(d2)):
                            d3 = d3 + d2[i]
                else:
                    return d1[1]
            else:
                return False
        else:
            if "." in host:
                d2 = str(host).split('.') #['xxx', 'com']
                if len(d2[-1]) == 2 or len(d2[-1]) == 3:
                    for i in range(0, len(d2) - 1):
                        d3 = d3 + d2[i]                        
                else:
                    for i in range(0, len(d2)):
                        d3 = d3 + d2[i]#print "d3 =", d3                        
            else:
                return host
        return d3

    def get_email(self, host, mailaccount):
        d3 = ''
        if 'www.' in host:
            d1 = str(host).split('www') #['www', 'xxx.com']
            if len(d1) > 1:
                d3 = str(mailaccount) + '@' + d1[1]
            else:
                return False
        else:
            d3 = str(mailaccount) + '@' + host
        return d3    

    def keymaker(self, quiet=None):
        path = self.cfg.get('PATH','SSLPATH')
        if os.path.isfile(os.path.join(str(path),self.host + ".crt")):
            print "\n"
            if quiet:
                confr = 'y'
            else:
                confr = raw_input(" File EXIST: (" + str(os.path.join(str(path),self.host + ".crt")) + "), Do you want to Overwrite file (y/n) ?: ")
            if confr == 'y' or confr == "Y":
                DOU = self.get_OU(self.host)
                DMail = self.get_email(self.host, 'root')
                if DOU != False:
                    OU = self.get_OU(self.host)
                else:
                    raise SyntaxWarning('Error making key (OU) ....')
                if DMail != False:
                    Mail = self.get_email(self.host, 'root')
                else:
                    raise SyntaxWarning('Error making key (Mail) ....')                
                cfgkey = self.make_key_config(2048, self.host, OU, self.host, Mail)
                os.system("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout d:\WWW\SSLCertificateKeyFile\\" + self.host + ".key -out " + str(path) + self.host + ".crt -config " + cfgkey)    
                return True
            elif confr == 'n' or confr == 'N':
                pass
            else:
                print "\n"
                print " You Not select y/n (SKIPPED)!"
                return False
        else:
            DOU = self.get_OU(self.host)
            DMail = self.get_email(self.host, 'root')
            if DOU != False:
                OU = self.get_OU(self.host)
            else:
                raise SyntaxWarning('Error making key (OU) ....')
            if DMail != False:
                Mail = self.get_email(self.host, 'root')
            else:
                raise SyntaxWarning('Error making key (Mail) ....')                
            cfgkey = self.make_key_config(2048, self.host, OU, self.host, Mail)
            os.system("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout d:\WWW\SSLCertificateKeyFile\\" + self.host + ".key -out " + str(path) + self.host + ".crt -config " + cfgkey)          
            #os.system("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout d:\WWW\SSLCertificateKeyFile\\" + self.host + ".key -out " + str(path) + self.host + ".crt")
            return True

    def includeVhost(self):
        #print self.cfg.get('PATH','VHOST')
        self.qVPath()
        insertFile = "Include " + str(self.cfg.get('PATH','MASTER')).replace("\\","/")  + "/" + self.host + ".conf"
        fd = open(self.qVPath(),'r+')
        fdd = fd.readlines()
        for i in fdd:
            if insertFile in i:
                print "\n"
                print " " + str(insertFile) + " has been inserted !"
                print "\n"
                fd.close()
                return False
        f = open(self.qVPath(), 'a')
        f.write("\n" + insertFile)
        f.close()
        return True

    def qMPath(self,path=None):
        """
        if path == None:
            if os.path.isdir(self.cfg.get('PATH','MASTER')):
                return self.cfg.get('PATH','MASTER')
            else:
                MPath = raw_input(" Please Definition Where Master Path to Write/Save File\n (example: /etc/apache/conf/extras|c:\apache\conf\extras): ")
                self.writeconf('PATH','MASTER',MPath)
                return MPath
        else:
            path = path
            self.writeconf('PATH','MASTER',path)
            return path
        """
        if path == None:
            if os.path.isdir(self.cfg.get('PATH','MASTER')):
                return self.cfg.get('PATH','MASTER')
            else:
                MPath = raw_input(" Please Definition Where Master Path to Write/Save File\n (example: /etc/apache/conf/extras|c:\apache\conf\extras): ")
                self.writeconf('PATH','MASTER',MPath)
                return MPath
        else:
            path = path
            self.writeconf('PATH','MASTER',path)
            return path

    def qVPath(self,path=None):
        """
        if path == None:
            if os.path.isfile(self.cfg.get('PATH','VHOST')):
                return self.cfg.get('PATH','VHOST')
            else:
                MPath = raw_input(" Please Definition Where Vhost Master Path to Write/Save File\n (example: /etc/apache/conf/extras/httpd-vhosts.conf|Apache2.4.4\conf\extra\httpd-vhosts.conf): ")
                self.writeconf('PATH','VHOST',MPath)
                return MPath
        else:
            path = path
            self.writeconf('PATH','VHOST',path)
            return path
        """
        if path == None:
            if os.path.isfile(self.cfg.get('PATH','VHOST')):
                return self.cfg.get('PATH','VHOST')
            else:
                MPath = raw_input(" Please Definition Where Vhost Master Path to Write/Save File\n (example: /etc/apache/conf/extras/httpd-vhosts.conf|Apache2.4.4\conf\extra\httpd-vhosts.conf): ")
                self.writeconf('PATH','VHOST',MPath)
                return MPath
        else:
            path = path
            self.writeconf('PATH','VHOST',path)
            return path    

    def checkSVC(self,svcname, quiet=None):
        #print "quite 0 =", quiet
        try:
            srvname = Cservice.WService(svcname)
            if srvname.status() == "RUNNING":
                if quiet:
                    s = "y"
                    print "Service " + str(svcname) + " is RUNNING and will be RESTART it !: "
                else:
                    s = raw_input(" Service " + str(svcname) + " is RUNNING, Do you want to RESTART it (y/n): ")
                if s == "y" or s == "Y":
                    srvname.restart()
                    print "\n"
                    print "\t Service " + str(svcname) + " is " + srvname.status()
                    print "\n"
                    print "--------------script by LICFACE <licface@yahoo.com>---------------"                    
                    return True
                elif s == "n" or s == "N":
                    print "\n"
                    print "\t Service " + str(svcname) + " is " + srvname.status()
                    print "\n"
                    print "--------------script by LICFACE <licface@yahoo.com>---------------"
                    return True
                else:
                    print "\n"
                    print "\t Service " + str(svcname) + " is " + srvname.status()
                    print "\n"
                    print " You Not select y/n (SKIPPED)!"
                    print "\n"
                    print "--------------script by LICFACE <licface@yahoo.com>---------------"                    
                    return False
            elif srvname.status() == "STARTING":
                print "\t Service " + str(svcname) + " is " + srvname.status()
                print "\t Plase Wait a while ... "
            else:
                if quiet:
                    s = "y"
                    print "Service " + str(svcname) + " is STOPPED and will be START it !: "
                else:
                    s = raw_input(" Service " + str(svcname) + " is STOPPED, Do you want to START it (y/n): ")
                if s == "y" or s == "Y":
                    srvname.start()
                    print "\n"
                    print "\t Service " + str(svcname) + " is " + srvname.status()
                    print "\n"
                    print "--------------script by LICFACE <licface@yahoo.com>---------------"                    
                    return True
                elif s == "n" or s == "N":
                    print "\n"
                    print "\t Service " + str(svcname) + " is " + srvname.status()
                    print "\n"
                    print "--------------script by LICFACE <licface@yahoo.com>---------------"
                    return True
                else:
                    print "\n"
                    print "\t Service " + str(svcname) + " is " + srvname.status()
                    print "\n"
                    print " You Not select y/n (SKIPPED)!"
                    print "\n"
                    print "--------------script by LICFACE <licface@yahoo.com>---------------"                    
                    return False
            return True            
        except SyntaxError:
            APath = raw_input(" Please Definition Web Server Service Name\n (example: apache2.4|httpd|xginx): ")
            self.writeconf('SERVER','SERVERSVC',APath)
            self.checkSVC(APath, quiet)    
        return False

    def qAPath(self,sname=None, quiet=None):
        if sname == None:
            if len(self.cfg.get('SERVER','SERVERSVC')) < 1 or self.cfg.get('SERVER','SERVERSVC') == None or self.cfg.get('SERVER','SERVERSVC') == '':
                APath = raw_input(" Please Definition Web Server Service Name\n (example: apache2.4|httpd|xginx): ")
                self.writeconf('SERVER','SERVERSVC',APath)
                self.checkSVC(APath, quiet)
            else:
                svcname = self.cfg.get('SERVER','SERVERSVC')
                self.checkSVC(svcname, quiet)   
        else:
            self.checkSVC(sname, quiet)

    def vhost(self, host, path ,email="root@", dindex=None, checkpass=None, adddns=None, verbosity=None, quiet=None):
        print "quiet 1 =", quiet
        if self.host == None:
            self.host = host
        if self.path == None:
            self.path = path
        if "root@" not in email:
            self.email = email
        else:
            self.email = email + host
        self.masterpath = self.qMPath()
        if dindex != None:
            vhostNote = """<VirtualHost *:80>
    ServerAdmin %s
    DocumentRoot "%s"
    ServerName %s
    ServerAlias www.%s
    ErrorLog "logs/%s-error.log"
    CustomLog "logs/%s-access.log" common
    DirectoryIndex %s
</VirtualHost>

<VirtualHost *:443>
    SSLEngine on
    SSLProxyEngine off
    SSLOptions +StrictRequire
    SSLVerifyClient none
    <Directory />
        SSLRequireSSL
    </Directory>

    SSLProtocol -all +TLSv1 +SSLv3
    SSLCipherSuite HIGH:MEDIUM:!aNULL:+SHA1:+MD5:+HIGH:+MEDIUM
    SSLCertificateFile "d:/WWW/SSLCertificateKeyFile/%s.crt"
    SSLCertificateKeyFile  "d:/WWW/SSLCertificateKeyFile/%s.key"
    #SSLSessionCache        "shmcb:c:/wamp/bin/apache/Apache2.4.4/logs/ssl_scache(512000)"
    SSLSessionCacheTimeout 600   
    <IfModule mime.c>
        AddType application/x-x509-ca-cert      .crt
        AddType application/x-pkcs7-crl         .crl
    </IfModule>
    SetEnvIf User-Agent ".*MSIE.*" nokeepalive ssl-unclean-shutdown downgrade-1.0 force-response-1.0
    ServerName %s
    ServerAlias www.%s
    ErrorLog "logs/%s.https-error.log"
    CustomLog "logs/%s.https-access.log" common
</VirtualHost>
"""%(self.email,self.path,self.host,self.host,self.host,self.host, dindex, self.host,self.host,self.host,self.host,self.host,self.host)
        else:
            vhostNote = """<VirtualHost *:80>
    ServerAdmin %s
    DocumentRoot "%s"
    ServerName %s
    ServerAlias www.%s
    ErrorLog "logs/%s-error.log"
    CustomLog "logs/%s-access.log" common
</VirtualHost>

<VirtualHost *:443>
        SSLEngine on
        SSLProxyEngine off
        SSLOptions +StrictRequire
        SSLVerifyClient none
    <Directory />
        SSLRequireSSL
    </Directory>

    SSLProtocol -all +TLSv1 +SSLv3
    SSLCipherSuite HIGH:MEDIUM:!aNULL:+SHA1:+MD5:+HIGH:+MEDIUM
        SSLCertificateFile "d:/WWW/SSLCertificateKeyFile/%s.crt"
        SSLCertificateKeyFile  "d:/WWW/SSLCertificateKeyFile/%s.key"
        #SSLSessionCache        "shmcb:c:/wamp/bin/apache/Apache2.4.4/logs/ssl_scache(512000)"
        SSLSessionCacheTimeout 600   
        <IfModule mime.c>
        AddType application/x-x509-ca-cert      .crt
        AddType application/x-pkcs7-crl         .crl
    </IfModule>
        SetEnvIf User-Agent ".*MSIE.*" nokeepalive ssl-unclean-shutdown downgrade-1.0 force-response-1.0
        ServerName %s
        ServerAlias www.%s
        ErrorLog "logs/%s.https-error.log"
        CustomLog "logs/%s.https-access.log" common
</VirtualHost>
"""%(self.email,self.path,self.host,self.host,self.host,self.host,self.host,self.host,self.host,self.host,self.host,self.host)
        vhostFile = open(os.path.join(self.masterpath,host)+".conf","w")
        vhostFile.write(vhostNote)
        vhostFile.close()
        if adddns == False:
            addhost.main(self.host)
        self.keymaker(quiet=quiet)
        #print self.includeVhost()
        if self.includeVhost() == False:
            pass
        else:
            self.includeVhost()
        self.qAPath(quiet=quiet)

    def proxy(self,host,port,email="root@", ip=None, adddns=None, quiet=None):
        if self.host == None:
            self.host = host
        if ip == None:
            ip = path = self.cfg.get('SERVER','HOST')
        if "root@" not in email:
            self.email = email
        else:
            self.email = email + host
        if ":" in  host:
            port_pre = str(str(host).split(":")[1]).strip()
            if port_pre != None or port_pre != "":
                port = port_pre
            else:
                port = port
        else:
            port = port        

        proxyNote = """<VirtualHost *:80>
	<Proxy *:%s>
		Require all granted
	</Proxy>
    ServerAdmin %s
	ProxyPreserveHost On
	ProxyPass / http://%s:%s/
	ProxyPassReverse / http://%s:%s/
	ServerName %s
	ServerAlias www.%s
	ErrorLog "logs/%s-error.log"
	CustomLog "logs/%s-access.log" common
</VirtualHost>

<VirtualHost *:443>
        <Proxy *:%s>
            Require all granted
        </Proxy>
        SSLEngine on
        SSLProxyEngine off
        SSLOptions +StrictRequire
        SSLVerifyClient none
    <Directory />
        SSLRequireSSL
    </Directory>

    SSLProtocol -all +TLSv1 +SSLv3
    SSLCipherSuite HIGH:MEDIUM:!aNULL:+SHA1:+MD5:+HIGH:+MEDIUM
        SSLCertificateFile "d:/WWW/SSLCertificateKeyFile/%s.crt"
        SSLCertificateKeyFile  "d:/WWW/SSLCertificateKeyFile/%s.key"
        #SSLSessionCache        "shmcb:c:/wamp/bin/apache/Apache2.4.4/logs/ssl_scache(512000)"
        SSLSessionCacheTimeout 600   
        <IfModule mime.c>
        AddType application/x-x509-ca-cert      .crt
        AddType application/x-pkcs7-crl         .crl
    </IfModule>
        SetEnvIf User-Agent ".*MSIE.*" nokeepalive ssl-unclean-shutdown downgrade-1.0 force-response-1.0
        ProxyPreserveHost On
        ProxyPass / http://%s:%s/
        ProxyPassReverse / http://%s:%s/
        ServerName %s
        ServerAlias www.%s
        ErrorLog "logs/%s.https-error.log"
        CustomLog "logs/%s.https-access.log" common
</VirtualHost>
"""%(port,self.email,ip,port, ip,port,self.host,self.host,self.host, self.host,port,self.host,self.host,ip,port,ip,port,self.host,self.host,self.host,self.host)
        self.masterpath = self.qMPath()
        proxyFile = open(os.path.join(self.masterpath, str(host) + ".conf"),"w")
        proxyFile.write(proxyNote)
        proxyFile.close()
        if adddns == False or adddns == None:
            addhost.main(self.host)
        self.keymaker(quiet=quiet)
        if self.includeVhost() == False:
            pass
        else:
            self.includeVhost()
        self.qAPath(quiet=quiet)

    def usage(self):
        parser = optparse.OptionParser()
        parser.add_option("-v","--verbosity", help="Show process running", action="store_true")
        parser.add_option("-V","--version", help="Show version", action="store_true")
        #parser.add_option('TYPE', help="Type (vhost|proxy)", action="store", type=str)
        #parser.add_option("HOST", help="Add host (example: myhost.com)", action="store", type=str)
        parser.add_option('-e', '--email',help="Email ServerAdmin (example: root@myhost.com), default: root@HOST", action="store", default='')
        parser.add_option('-n', '--nodns', help="Not add/generate DNS Host", action="store_true")
        parser.add_option('-a', "--ip", help="IP Host Proxy Reverse/Pass to used ",action="store", type=str)
        parser.add_option('-p', "--port", help="Port Proxy Reverse/Pass to used ",action="store", type=int, default=80)
        #parser.add_option("PATH", help="Path where Document Root or File Website/Site is stored\nThis used for VirtualHost", action="store", type=str)
        parser.add_option("-i", "--directoryindex", help="Add section \"DirectoryIndex\"", action="store", type=str)
        parser.add_option("-q", "--quiet", help="bypass All of confirmation", action="store_true")
        args, argv = parser.parse_args()
        print "args =", args
        print "argv =", argv
        if args.version:
            print "Version:", __version__+"("+__test__+")"
        if len(sys.argv) < 2:
            print "\n"
            parser.print_help()
        else:
            if str("vhost").strip() in argv:
                #print "AAAAAAAAAAAAAAAAA"
                if len(argv) > 2:
                    dir_temp = []
                    for i in argv:
                        if os.path.isdir(i):
                            dir_temp.append(i)
                    #print "dir_temp =", dir_temp
                    if len(dir_temp) > 1:
                        return "\tPlease make sure where is data web stored !"
                    else:
                        PATH = dir_temp[0]
                    for a in argv:
                        if  "." in a:
                            HOST = a
                    #print "HOST =", HOST            
                    if args.directoryindex:
                        self.vhost(HOST, PATH, dindex=args.directoryindex, 
adddns=args.nodns, verbosity=True, quiet=args.quiet)
                    else:
                        self.vhost(HOST, PATH, adddns=args.nodns, quiet=args.quiet)
                else:
                    parser.print_help()
                        
            elif str("proxy").strip() in argv: #Proxy
                if len(argv) > 2:
                    dir_temp = []
                    for i in argv:
                        if os.path.isdir(i):
                            return "\tPlease make sure whereis data web stored !"
                    for a in argv:
                        check_host = re.split("\.", a)
                        check_host_bool = []
                        if len(check_host) == 4:
                            for b in check_host:
                                if str(b).isdigit():
                                    check_host_bool.append(True)
                                else:
                                    check_host_bool.append(False)
                            if "False" in check_host_bool:
                                return "\tPlease insert you IP HOST number !"
                            else:
                                HOST = a                
                    if args.port:
                        if isinstance(args.port, int):
                            if args.email:
                                if "@" in args.email:
                                    if args.ip:
                                        self.proxy(HOST, str(args.port), args.email, 
ip=args.ip, adddns=args.nodns, quiet=args.quiet)
                                    else:
                                        self.proxy(HOST, str(args.port), args.email, adddns=args.nodns, quiet=args.quiet)
                                else:
                                    print "\n"
                                    print "\t Please Insert Correct EMAIL !"
                                    print "\n"
                                    parser.print_help()
                            else:
                                args = parser.parse_args()
                                if args.ip:
                                    self.proxy(HOST, str(args.port), ip=args.ip, quiet=args.quiet)
                                else:
                                    self.proxy(args.HOST, str(args.port), quiet=args.quiet)
                        else:
                            print "\n"
                            print "\tPlease insert PORT Number !"
                            print "\n"
                            parser.print_help()
                    else:
                        print "\n"
                        print "\tPlease insert PORT Number !"
                        print "\n"
                        parser.print_help()
                else:
                    parser.print_help()
            else:
                #data_args = ['-h', '--help', '-v', '--verbosity', '-V', '--version', '-e', '--email', '-n', '--nodns', '-a', '--ip', '-p', '--port', '-i', '--directoryindex']
                if len(argv) == 0:
                    parser.print_help()
                else:
                    print "\n"
                    print "\tPlase select your TYPE !"
                    print "\n"
                    parser.print_help()

if __name__ == "__main__":
    vhostmaker = maker()
    vhostmaker.usage()
    #subprocess.Popen([addhost.main([str(sys.argv[1])])])
    #addhost.main([sys.argv[1]])
    #print vhostmaker.get_key(1024, "rere", "ID", "WestJava", "Bandung", "LICFACE", "licface.net", "www.licface.net", "root@licface.net")
    #print vhostmaker.get_OU('licface')
    #vhostmaker.checkSVC()
    #vhostmaker.includeVhost()