import os
import sys
import re
import optparse
import string
import Cservice
import ConfigParser
#import subprocess
import addhostx as addhost
import sendgrowl
import logging
import inspect
import threading
import traceback

__author__ = "licface@yahoo.com"
__version__ = "1.6"
__test__ = "0.2"
__sdk__ = "2.7"
__build__ =  "windows"
__platform_test__ = 'nt'
__changelog__ = 'repair all of verbosity, add logging details'
__build_date__ = '2014-09-13: 10:35:20'

class maker:
    def __init__(self, host=None,path=None,email=None):
        self.host = host
        self.path = path
        self.email = email     
        self.masterpath = None
        self.FILECONF = os.path.join(os.path.dirname(__file__),"conf.ini")
        self.cfg = ConfigParser.RawConfigParser()
        self.cfg.read(self.FILECONF)
        self.cfgsave = ConfigParser.SafeConfigParser()
        self.cfgsave.read(self.FILECONF)
        self.format_logging = logging.Formatter("%(levelname)s (%(levelno)s): %(asctime)-15s;  def:%(funcName)s; line:%(myline)s; %(message)s; created:%(created)f", "%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger('vhostmaker')
        self.logg = logging.StreamHandler()
        self.logg.setFormatter(self.format_logging)
        self.logger.addHandler(self.logg)
        
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
                print "\n"
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
                os.system("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout d:\WWW\SSLCertificateKeyFile\\" + self.host + ".key -out " + os.path.join(str(path), self.host + ".crt") + "  -config " + cfgkey)    
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

    def includeVhost(self, verbosity=None):
        #print self.cfg.get('PATH','VHOST')
        self.qVPath()
        insertFile = "Include " + str(self.cfg.get('PATH','MASTER')).replace("\\","/")  + "/" + self.host + ".conf"
        fd = open(self.qVPath(),'r+')
        fdd = fd.readlines()
        check_insert = []
        for i in fdd:
            if insertFile in i:
                datamsg = " " + str(insertFile) + " has been inserted !"
                self.logme(str(datamsg), verbosity, 'warning')
                print " " + str(insertFile) + " has been inserted !"
                return None
                fd.close()
                check_insert.append(True)
        if len(check_insert) > 0:pass
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
        try:
            srvname = Cservice.WService(svcname)
            if srvname.status() == "RUNNING":
                if quiet:
                    s = "y"
                    print " Service " + str(svcname) + " is RUNNING and will be RESTART it !: "
                else:
                    print "\n"
                    s = raw_input(" Service " + str(svcname) + " is RUNNING, Do you want to RESTART it (y/n): ")
                if s == "y" or s == "Y":
                    p = threading.Thread(name="apache service control", target=srvname.restart)
                    p.daemon = True
                    p.start()
                    #p.join()
                    #result = queue.get()
                    #print result
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
                    print " Service " + str(svcname) + " is %s and will be START it !: " % (str(srvname.status()))
                else:
                    print "\n"
                    s = raw_input(" Service " + str(svcname) + " is STOPPED, Do you want to START it (y/n): ")
                if s == "y" or s == "Y":
                    p = threading.Thread(name="apache service control", target=srvname.start)
                    p.daemon = True
                    p.start()
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
            
    def logme(self, msg, verbosity=None, log_type=None, exc_info=None):
        myextra = {'myline': str(inspect.currentframe().f_back.f_lineno)}
        if verbosity == True:
            if log_type == 'info':
                self.logger.setLevel(logging.INFO)
                self.logg.setLevel(logging.INFO)
                if exc_info:
                    return self.logger.info('Error: %s'% exc, exc_info=True, extra=myextra)
                else:
                    return self.logger.info(msg, extra=myextra)
            elif log_type == 'warning':
                self.logger.setLevel(logging.WARNING)
                self.logg.setLevel(logging.WARNING)
                if exc_info:
                    return self.logger.warning('Error: %s'% exc, exc_info=True, extra=myextra)
                else:
                    return self.logger.warning(msg, extra=myextra)
            elif log_type == 'error':
                print "SSSS"
                self.logger.setLevel(logging.ERROR)
                self.logg.setLevel(logging.ERROR)
                print "msg error =", msg
                if exc_info:
                    return self.logger.error('Error: %s'% exc, exc_info=True, extra=myextra)
                else:
                    return self.logger.error(msg, extra=myextra)
            elif log_type == 'critical':
                self.logger.setLevel(logging.CRITICAL)
                self.logg.setLevel(logging.CRITICAL)
                if exc_info:
                    return self.logger.critical('Error: %s'% exc, exc_info=True, extra=myextra)
                else:
                    return self.logger.critical(msg, extra=myextra)
            elif log_type == 'debug':
                self.logger.setLevel(logging.DEBUG)
                self.logg.setLevel(logging.DEBUG)
                if exc_info:
                    return self.logger.debug('Error: %s'% exc, exc_info=True, extra=myextra)
                else:
                    return self.logger.debug(msg, extra=myextra)
            else:
                self.logger.setLevel(logging.DEBUG)
                self.logg.setLevel(logging.DEBUG)
                if exc_info:
                    return self.logger.debug('Error: %s'% exc, exc_info=True, extra=myextra)
                else:
                    return self.logger.debug(msg, extra=myextra)

    def vhost(self, host, path ,email="root@", dindex=None, checkpass=None, adddns=None, verbosity=None, quiet=None):
        try:
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
            self.logme('open file vhost mode: write', verbosity, 'info')
            vhostFile = open(os.path.join(self.masterpath,host)+".conf","w")
            self.logme('write file vhost', verbosity, 'info')
            vhostFile.write(vhostNote)
            self.logme('close file vhost', verbosity, 'info')
            vhostFile.close()
            if adddns == None:
                self.logme('add host', verbosity, 'info')
                addhost.main(self.host)
            self.logme('make SSL Key', verbosity, 'info')
            self.keymaker(quiet=quiet)
            #print self.includeVhost()
            self.logme('Verify file vhost apache config', verbosity, 'info')
            if self.includeVhost(verbosity=verbosity) == True:
                self.includeVhost(verbosity=verbosity)
            self.qAPath(quiet=quiet)
        except:
            self.logme('', verbosity, 'error', True)

    def proxy(self,host,port,email="root@", ip=None, adddns=None, quiet=None, verbosity=None):
        try:
            myname = sys._getframe().f_code.co_name
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
            self.logme('verify masterpath', verbosity, 'info')
            self.masterpath = self.qMPath()
            self.logme('read  config temp', verbosity, 'info')
            proxyFile = open(os.path.join(self.masterpath, str(host) + ".conf"),"w")
            self.logme('write config temp', verbosity, 'info')
            proxyFile.write(proxyNote)
            self.logme('close config temp', verbosity, 'info')
            proxyFile.close()    
            if adddns == None:
                addhost.main(self.host)
            self.keymaker(quiet=quiet)
            #if self.includeVhost(verbosity=verbosity) == True:
            self.includeVhost(verbosity=verbosity)
            self.qAPath(quiet=quiet)
        except Exception, exc:
            print "\n"
            myextra = {'myline': str(inspect.currentframe().f_back.f_lineno)}
            self.logger.error('Error: %s'% exc, exc_info=True, extra=myextra)

    def usage(self):
        parser = optparse.OptionParser()
        parser.add_option("-v", "--verbosity", help="Show process running", action="store_true")
        parser.add_option("-V", "--version", help="Show version", action="store_true")
        parser.add_option('-e', '--email',help="Email ServerAdmin (example: root@myhost.com), default: root@HOST", action="store", default='')
        parser.add_option('-n', '--nodns', help="Not add/generate DNS Host", action="store_true")
        parser.add_option('-a', "--ip", help="IP Host Proxy Reverse/Pass to used ",action="store", type=str)
        parser.add_option('-p', "--port", help="Port Proxy Reverse/Pass to used ",action="store", type=int, default=80)
        parser.add_option("-i", "--directoryindex", help="Add section \"DirectoryIndex\"", action="store", type=str)
        parser.add_option("-q", "--quiet", help="bypass All of confirmation", action="store_true")
        parser.add_option("-c", "--changelog", help="Show current Changelog", action="store_true")
        args, argv = parser.parse_args()
        
        if args.changelog:
            print "\n"
            print "\tChangelog: \"" + __changelog__ + "\" (%s)" %(__build_date__)
            print "\n"
        if args.version:
            print "\n"
            print "\tVersion:", __version__+"("+__test__+")"
            print "\n"
        if len(sys.argv) < 2:
            print "\n"
            parser.print_help()
        else:
            #print "argv =", argv
            #print "args =", args
            if str("vhost").strip() in argv:
                if len(argv) > 2:
                    dir_temp = []
                    for i in argv:
                        if os.path.isdir(i):
                            dir_temp.append(i)
                    if len(dir_temp) > 1:
                        self.logme("Please make sure where is data web stored !", verbosity, 'critical')
                        return "\tPlease make sure where is data web stored !"
                    else:
                        PATH = dir_temp[0]
                    for a in argv:
                        if  "." in a:
                            if os.path.isdir(a) == False:
                                HOST = a           
                    if args.directoryindex:
                        self.vhost(HOST, PATH, dindex=args.directoryindex, 
adddns=args.nodns, verbosity=True, quiet=args.quiet)
                    else:
                        self.vhost(HOST, PATH, adddns=args.nodns, quiet=args.quiet)
                else:
                    parser.print_help()
                        
            elif str("proxy").strip() in argv: #Proxy
                #print "AAAA"
                #print "argv proxy =", argv
                #print "args proxy =", args                
                if len(argv) > 1:
                    dir_temp = []
                    for i in argv:
                        if os.path.isdir(i):
                            self.logme("Please make sure whereis data web stored !", verbosity=args.verbosity, log_type='error')
                            return "\tPlease make sure whereis data web stored !"
                    for a in argv:
                        check_host = re.split("\.", a)
                        #print "check_host =", check_host
                        check_host_bool = []
                        for d in check_host:
                            if "com" in str(d).strip():
                                HOST = a
                            elif "net" in str(d).strip():
                                HOST = a
                            elif "org" in str(d).strip():
                                HOST = a
                            elif "edu" in str(d).strip():
                                HOST = a
                            elif "id" in str(d).strip():
                                HOST = a
                            elif "us" in str(d).strip():
                                HOST = a
                            else:
                                HOST = ''
                                #self.logme("Please definition your HOST name !", args.verbosity, 'error')
                                #return "\tPlease definition your HOST name !"
                    #print "check_host =", check_host
                    if HOST == '':
                        self.logme("Please definition your HOST name !", args.verbosity, 'error')
                    else:
                        self.logme("set HOST: %s"%(HOST), args.verbosity, 'info')
                    if args.port:
                        if isinstance(args.port, int):
                            if args.email:
                                if "@" in args.email:
                                    if args.ip:
                                        self.proxy(HOST, str(args.port), args.email, 
ip=args.ip, adddns=args.nodns, quiet=args.quiet, verbosity=args.verbosity)
                                    else:
                                        self.proxy(HOST, str(args.port), args.email, adddns=args.nodns, quiet=args.quiet, verbosity=args.verbosity)
                                else:
                                    print "\n"
                                    print "\t Please Insert Correct EMAIL !"
                                    print "\n"
                                    parser.print_help()
                            else:
                                if args.ip:
                                    self.proxy(HOST, str(args.port), ip=args.ip, quiet=args.quiet, verbosity=args.verbosity)
                                else:
                                    self.proxy(HOST, str(args.port), quiet=args.quiet, verbosity=args.verbosity)
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