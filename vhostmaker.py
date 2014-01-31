import os
import sys
import argparse
import string
import conf
import Cservice
from iniparse import INIConfig

__author__ = "licface@yahoo.com"
__version__ = "0.1"
__test__ = "0.1"
__sdk__ = "2.7"
__platform_test__ = 'nt'

class maker:
    def __init__(self, host=None,path=None,email=None):
        self.host = host
        self.path = path
        self.email = email     
        self.masterpath = None
        
    def includeVhost(self):
        cfg = INIConfig(file(os.path.join(os.path.dirname(__file__),"conf.ini")))
        self.qVPath()
        f = open(cfg.PATH.VHOST,'a')
        f.write("Include " + str(cfg.PATH.MASTER).replace("\\","/") + "/" + self.host + ".conf")
        f.close()
        return True
    
    def qMPath(self,path=None):
        if path == None:
            cfg = INIConfig(file(os.path.join(os.path.dirname(__file__),"conf.ini")))
            if os.path.isdir(cfg.PATH.MASTER):
                return cfg.PATH.MASTER
            else:
                MPath = raw_input(" Please Definition Where Master Path to Write/Save File\n (example: /etc/apache/conf/extras|c:\apache\conf\extras): ")
                cfg.PATH.MASTER = MPath
                return MPath
        else:
            path = path
            return path
        
    def qVPath(self,path=None):
        if path == None:
            cfg = INIConfig(file(os.path.join(os.path.dirname(__file__),"conf.ini")))
            if os.path.isfile(cfg.PATH.VHOST):
                return cfg.PATH.VHOST
            else:
                MPath = raw_input(" Please Definition Where Vhost Master Path to Write/Save File\n (example: /etc/apache/conf/extras/httpd-vhosts.conf|Apache2.4.4\conf\extra\httpd-vhosts.conf): ")
                cfg.PATH.VHOST = MPath
                return MPath
        else:
            path = path
            return path    
        
    def checkSVC(self,svcname):
        cfg = INIConfig(file(os.path.join(os.path.dirname(__file__),"conf.ini")))
        srvname = Cservice.WService(svcname)
        if srvname.getname()[0] != None:
            if srvname.status() == "RUNNING":
                s = raw_input(" Service %s is %s, Do you want to RESTART it (y/n): ")
                if s == "y" or s == "Y":
                    srvname.restart()
                elif s == "n" or s == "N":
                    pass
                else:
                    print "\n"
                    print " You Not select y/n (SKIPPED)!"
            else:
                s = raw_input(" Service %s is %s, Do you want to START it (y/n): ")
                if s == "y" or s == "Y":
                    srvname.start()
                elif s == "n" or s == "N":
                    pass
                else:
                    print "\n"
                    print " You Not select y/n (SKIPPED)!"
            return True
        else:
            APath = raw_input(" Please Definition Web Server Service Name\n (example: apache2.4|httpd|xginx): ")
            cfg.SERVER.SERVERSVC = str(APath)
            self.checkSVC(APath)              
        return False
    
    def qAPath(self,servicename=None):
        cfg = INIConfig(file(os.path.join(os.path.dirname(__file__),"conf.ini")))
        if servicename == None:
            if len(cfg.SERVER.SERVERSVC) > 1 or cfg.SERVER.SERVERSVC != None or cfg.SERVER.SERVERSVC != '':
                svcname = Cservice.WService(cfg.SERVER.SERVERSVC)
                self.checkSVC(svcname)
            else:
                APath = raw_input(" Please Definition Web Server Service Name\n (example: apache2.4|httpd|xginx): ")
                cfg.SERVER.SERVERSVC = str(APath)
                self.checkSVC(APath)              
        else:
            svcname = Cservice.WService(servicename)
            self.checkSVC(svcname)
            
    def vhost(self, host,path,email="root@"):
        if self.host == None:
            self.host = host
        if self.path == None:
            self.path = path
        if "root@" not in email:
            self.email = email
        else:
            self.email = email + host

        self.masterpath = self.qMPath()
        vhostNote = """<VirtualHost *:80>
    ServerAdmin %s
    DocumentRoot "%s"
    ServerName %s
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
"""%(self.email,self.path,self.host,self.host,self.host,self.host,self.host,self.host,self.host,self.host,self.host)
        vhostFile = open(os.path.join(self.masterpath,host)+".conf","w")
        vhostFile.write(vhostNote)
        self.keymaker()
        self.qAPath()
        self.includeVhost()
        
    def proxy(self,host,port,email="root@"):
        if self.host == None:
            self.host = host
        if "root@" not in email:
            self.email = email
        else:
            self.email = email + host
        port_pre = str(str(host).split(":")[1]).strip()
        if port_pre != None or port_pre != "":
            port = port_pre
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
        <Proxy *:$s>
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
"""%(port,self.email,self.host,port,self.host,port,self.host,self.host,self.host,self.host,port,self.host,self.host,self.host,port,self.host,port,self.host,self.host,self.host,self.host)
        proxyFile = open(os.path.join(self.masterpath,host)+".conf","w")
        proxyFile.write(proxyNote)    
        self.keymaker()
        self.qAPath()
        self.includeVhost()
        
    def keymaker(self):
        os.system("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout d:\WWW\SSLCertificateKeyFile\\" + self.host + ".key -out d:\WWW\SSLCertificateKeyFile\\" + self.host + ".crt")
        
    def serviceConf(self):
        serviceName = Cservice.WService()

    def usage(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-v","--verbosity", help="Show process running", action="store_true")
        parser.add_argument('TYPE', help="Type (vhost|proxy)", action="store", type=str)
        parser.add_argument("HOST", help="Add host (example: myhost.com)", action="store", type=str)
        parser.add_argument("PATH", help="Path where Document Root or File Website/Site is stored\nThis used for VirtualHost", action="store", type=str)
        parser.add_argument("PORT", help="Port Proxy Reverse/Pass to used ",action="store", type=int, default=80)
        parser.add_argument('EMAIL',help="Email ServerAdmin (example: root@myhost.com), default: root@HOST", action="store", default='')

        if len(sys.argv) < 2:
            print "\n"
            parser.print_help()
        else:
            if sys.argv[1] == "vhost":
                parser2 = argparse.ArgumentParser()
                parser2.add_argument("-v","--verbosity", help="Show process running", action="store_true")
                parser2.add_argument('TYPE', help="Type (vhost|proxy)", action="store", type=str)
                parser2.add_argument("HOST", help="Add host (example: myhost.com)", action="store", type=str)
                parser2.add_argument("PATH", help="Path where Document Root or File Website/Site is stored\nThis used for VirtualHost", action="store", type=str)
                if len(sys.argv) > 2:
                    if len(sys.argv) > 3:
                        args = parser2.parse_args()
                        if os.path.isdir(args.PATH):
                            self.vhost(args.HOST,args.PATH)
                        else:
                            print "\n"
                            print "\tPlease Insert Correct PATH !"
                            print "\n"
                            parser.print_help()
                    else:
                        print "\n"
                        print "\tPlease Insert your PATH !"
                        print "\n"
                        parser.print_help()                        
                else:
                    print "\n"
                    print "\tPlease Insert HOST name !"
                    print "\n"                    
                    parser.print_help()
            elif sys.argv[1] == "proxy":
                if os.path.isdir(sys.argv[2]):
                    if isinstance(sys.argv[4], int):
                        args = parser.parse_args()
                        if args.email:
                            if "@" in args.email:
                                self.proxy(args.host, str(args.port), args.email)
                            else:
                                print "\n"
                                print "\t Please Insert Correct EMAIL !"
                                print "\n"
                                parser.print_help()
                        else:
                            args = parser.parse_args()
                            self.proxy(args.host, str(args.port))                            
                    else:
                        print "\n"
                        print "\tPlease insert PORT Number !"
                        print "\n"
                        parser.print_help()
                else:
                    print "\n"
                    print "\tPlase Insert Correct PATH !"
                    print "\n"
                    parser.print_help()                    
            else:
                print "\n"
                print "\tPlase select your TYPE !"
                print "\n"
                parser.print_help()
                
if __name__ == "__main__":
    vhostmaker = maker()
    vhostmaker.usage()
    