import os
import sys
import re
import argparse
import string
if sys.platform == 'win32':
    import Cservice
    import addhostx as addhost
import ConfigParser
import subprocess
import logging
import inspect
import traceback

__author__ = "licface@yahoo.com"
__version__ = "1.9"
__test__ = "0.6"
__sdk__ = "2.7"
__build__ =  "windows"
__platform_test__ = 'nt'
__changelog__ = 're-add log function + func: search host'
__build_date__ = '2015-07-12: 21:18:10 (+8)'

class maker:
    def __init__(self, host=None,path=None,email=None):
        self.host = host
        self.path = path
        self.email = email     
        self.masterpath = None
        self.FILECONF = os.path.join(os.path.dirname(__file__),"vhostmaker.ini")
        self.cfg = ConfigParser.RawConfigParser()
        self.cfg.read(self.FILECONF)
        self.cfgsave = ConfigParser.SafeConfigParser()
        self.cfgsave.read(self.FILECONF)
        self.format_logging = logging.Formatter("%(levelname)s (%(levelno)s): %(asctime)-15s;  def:%(funcName)s; line:%(myline)s; %(message)s; created:%(created)f", "%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger('vhostmaker')
        self.logg = logging.StreamHandler()
        self.logg.setFormatter(self.format_logging)
        self.logger.addHandler(self.logg)
        self.apachesvc_name = self.getCfg('SERVER', 'serversvc')
        
    def getCfg(self, section, option):
        return str(self.cfg.get(section, option)).replace("\\","/")    

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
                os.system("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout %s\\" %(path) + self.host + ".key -out %s\\" %(path) + self.host + ".crt -config " + cfgkey)    
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
            # print "PATH SLL B =", path
            os.system("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout %s\\" %(path) + self.host + ".key -out %s\\" %(path) + self.host + ".crt -config " + cfgkey)          
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
                fd.close()
                return False
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
        if sys.platform == 'win32':
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
                        print " Service " + str(svcname) + " is %s and will be START it !: " % (str(srvname.status()))
                    else:
                        print "\n"
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

    def vhost(self, host, path ,email="root@", dindex=None, checkpass=None, adddns=None, verbosity=None, ipAll=None, passwd_sdns=None, quiet=None):
        try:
            if self.host == None:
                self.host = host
            if self.path == None:
                self.path = path
            if email == '' or email == None:
                email = "root@"            
            if "root@" not in email:
                self.email = email
            else:
                self.email = email + host
                
            self.masterpath = self.qMPath()
            SLL_PATH = self.getCfg('PATH', 'sslpath')
            if dindex != None:
                dindex = "DirectoryIndex %s" %(dindex)
            else:
                dindex = "# DirectoryIndex index.html"
                
            vhostNote = """<VirtualHost *:80>
ServerAdmin %s
DocumentRoot "%s"
ServerName %s
ServerAlias www.%s
ErrorLog "logs/%s-error.log"
CustomLog "logs/%s-access.log" common
%s
Options Indexes FollowSymLinks
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
    SSLCertificateFile "%s/%s.crt"
    SSLCertificateKeyFile  "%s/%s.key"
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
    """%(self.email,self.path,self.host,self.host,self.host,self.host, dindex, SLL_PATH, self.host, SLL_PATH,self.host,self.host,self.host,self.host,self.host)
            self.logme('open file vhost mode: write', verbosity, 'info')
            vhostFile = open(os.path.join(self.masterpath,host)+".conf","w")
            self.logme('write file vhost', verbosity, 'info')
            vhostFile.write(vhostNote)
            self.logme('close file vhost', verbosity, 'info')
            vhostFile.close()
            if adddns:
                self.logme('add host', verbosity, 'info')
                if sys.platform == 'win32':
                    addhost.main(ipAll, self.host, passwd_sdns)            
            self.logme('make SSL Key', verbosity, 'info')
            self.keymaker(quiet=quiet)
            self.logme('Verify file vhost apache config', verbosity, 'info')
            if self.includeVhost(verbosity=verbosity) == True:
                self.includeVhost(verbosity=verbosity)
            self.qAPath(quiet=quiet)
        except:
            self.logme('', verbosity, 'error', True)

    def proxy(self, host, port, email="root@", ip=None, adddns=None, verbosity=None, ipAll=None, passwd_sdns=None, quiet=None):
        try:
            if self.host == None:
                self.host = host
            if ip == None:
                ip = path = self.cfg.get('SERVER','HOST')
            if email == '' or email == None:
                email = "root@"
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
        SSLCertificateFile "%s/%s.crt"
        SSLCertificateKeyFile  "%s/%s.key"
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
        """%(port,self.email,ip,port, ip,port,self.host,self.host,self.host, self.host,port, self.getCfg('PATH', 'sslpath'), self.host, self.getCfg('PATH', 'sslpath'), self.host,ip,port,ip,port,self.host,self.host,self.host,self.host)
            self.logme('verify masterpath', verbosity, 'info')
            self.masterpath = self.qMPath()
            self.logme('read  config temp', verbosity, 'info')
            proxyFile = open(os.path.join(self.masterpath, str(host) + ".conf"),"w")
            self.logme('write config temp', verbosity, 'info')
            proxyFile.write(proxyNote)
            self.logme('close config temp', verbosity, 'info')
            proxyFile.close()    
            if adddns:
                if sys.platform == 'win32':
                    addhost.main(ipAll, self.host, passwd_sdns)
            self.keymaker(quiet=quiet)
            #if self.includeVhost(verbosity=verbosity) == True:
            self.includeVhost(verbosity=verbosity)
            self.qAPath(quiet=quiet)
        except Exception, exc:
            print "\n"
            myextra = {'myline': str(inspect.currentframe().f_back.f_lineno)}
            self.logger.error('Error: %s'% exc, exc_info=True, extra=myextra)

    def del_host(self, hostname, verbosity=None):
        PATH_MASTER = self.cfg.get('PATH', 'master')
        PATH_SSL = self.cfg.get("PATH", 'sslpath')
        listdir_MASTER = os.listdir(PATH_MASTER)
        listdir_SSL = os.listdir(PATH_SSL)
        for m in listdir_MASTER:
            if hostname + ".conf" in m:
                try:
                    os.remove(os.path.join(PATH_MASTER, m))
                except:
                    if verbosity:
                        print " ERROR:", traceback.format_exc()
    
        for s in listdir_SSL:
            if hostname + ".crt" in s:
                try:
                    os.remove(os.path.join(PATH_SSL, s))
                except:
                    if verbosity:
                        print " ERROR:", traceback.format_exc()
    
        for k in listdir_SSL:
            if hostname + ".key" in k:
                try:
                    os.remove(os.path.join(PATH_SSL, k))
                except:
                    if verbosity:
                        print " ERROR:", traceback.format_exc()        
    
    def usage(self):
        print "\n"
        prog = "vhostmaker"
        usage = "%s HOST TYPE [options]" %(prog)
        choices = ['vhost','proxy']
        usage_vhost="%s HOST vhost PATH [options]"%(os.path.basename(__file__))
        usage_proxy="%s HOST proxy [options]"%(os.path.basename(__file__))
        usage_dns="%s HOST dns [options]"%(os.path.basename(__file__))
        # usage_proxy="%s HOST [options]"%(os.path.basename(__file__))
    
        parser = argparse.ArgumentParser(prog=prog, usage=usage)
        # parser.add_argument('TYPE', help="Type (vhost|proxy)", action="store", choices=choices, type=str)
        parser.add_argument("HOST", help="Add host (example: myhost.com) or type 'update' for Update IP on SDSN Server (-U)", action="store", type=str)
        parser.add_argument('-e', '--email',help="Email ServerAdmin (example: root@myhost.com), default: root@HOST", action="store", default='root@')
        parser.add_argument('-q', '--quiet', help="by pass confirmation other options, by answer 'yes'", action="store_true")
        parser.add_argument('-n', '--adddns', help="Not generate DNS Host", action="store_true")
        parser.add_argument("-v","--verbosity", help="Show process running", action="store_true")
        parser.add_argument('-P', '--password', help='password access to SimpleDNS Server', default='blackid', action='store')
        parser.add_argument('-ipDNS', "--ipSDNS", help="IP SimpleDNS Server ", default='127.0.0.1', action="store", type=str)
        parser.add_argument('-d', '--delete', help="Del Host/Proxy", action="store_true")
        parser.add_argument('-s', '--search', help="Search Configuration of Host", action='store_true')
    
        subparser = parser.add_subparsers(title='TYPE', dest='TYPE')
    
        args_vhost = subparser.add_parser('vhost', help='Virtual Host Type "vhost"')
        args_vhost.usage = usage_vhost
        args_proxy = subparser.add_parser('proxy', help='Virtual Host Type "proxy"')
        args_proxy.usage = usage_proxy
        args_dns = subparser.add_parser('dns', help="Add Host to SDNS Server")
        args_dns.usage = usage_dns
    
        args_vhost.add_argument("-t", '--path', help="Path where Document Root or File Website/Site is stored\nThis used for VirtualHost", action="store", type=str, dest="PATH")
        args_vhost.add_argument("-i", "--directoryindex", help="Add section \"DirectoryIndex\"", action="store", type=str)
        args_vhost.add_argument('-q', '--quiet', help="by pass confirmation other options, by answer 'yes'", action="store_true")
        args_vhost.add_argument('-n', '--adddns', help="add generate DNS Host", action="store_true")
        args_vhost.add_argument("-v", "--verbosity", help="Show process running", action="store_true")
        args_vhost.add_argument('-ipDNS', "--ipSDNS", help="IP SimpleDNS Server ", default='127.0.0.1', action="store", type=str)
        args_vhost.add_argument('-P', '--password', help='password access to SimpleDNS Server', default='blackid', action='store')
        args_vhost.add_argument('-e', '--email',help="Email ServerAdmin (example: root@myhost.com), default: root@HOST", action="store", default='root@')
        args_vhost.add_argument('-d', '--delete', help="Del Host/Proxy", action="store_true")
        args_vhost.add_argument('-ip', "--ip", help="IP Host to used ",action="store", type=str)
        args_vhost.add_argument('-s', '--search', help="Search Configuration of Host", action='store_true')
    
        args_proxy.add_argument('-ip', "--ip", help="IP Host Proxy Reverse/Pass to used ",action="store", type=str)
        args_proxy.add_argument('-p', "--port", help="Port Proxy Reverse/Pass to used default: 80 ",action="store", type=int, default=80)
        args_proxy.add_argument('-q', '--quiet', help="by pass confirmation other options, by answer 'yes'", action="store_true")
        args_proxy.add_argument('-n', '--adddns', help="add generate DNS Host", action="store_true")
        args_proxy.add_argument("-v", "--verbosity", help="Show process running", action="store_true")
        args_proxy.add_argument('-ipDNS', "--ipSDNS", help="IP SimpleDNS Server default: 127.0.0.1", default='127.0.0.1', action="store", type=str)
        args_proxy.add_argument('-P', '--password', help='password access to SimpleDNS Server', default='blackid', action='store')
        args_proxy.add_argument('-e', '--email',help="Email ServerAdmin (example: root@myhost.com), default: root@HOST", action="store", default='root@')
        args_proxy.add_argument('-d', '--delete', help="Del Host/Proxy", action="store_true")
        args_proxy.add_argument('-s', '--search', help="Search Configuration of Host", action='store_true')
    
        args_dns.add_argument('-A', '--ipA', help='ip address A', action='store')
        args_dns.add_argument('-NS', '--ipNS', help='ip address NS', action='store')
        args_dns.add_argument('-WWW', '--ipWWW', help='ip address WWW', action='store')
        args_dns.add_argument('-MX', '--ipMX', help='ip address MX', action='store')
        args_dns.add_argument('-FTP', '--ipFTP', help='ip address FTP', action='store')
        args_dns.add_argument('-MAIL', '--ipMAIL', help='ip address MAIL', action='store')
        args_dns.add_argument('-e', '--email', help='email host server', action='store')
        args_dns.add_argument('-H', '--host', help='ip/hostname SimpleDNS Server', default='127.0.0.1', action='store')
        args_dns.add_argument('-P', '--password', help='password access to SimpleDNS Server', default='blackid', action='store')
        args_dns.add_argument('-p', '--port', help='port SimpleDNS Server, default=8053', default=8053, type=int, action='store')
        args_dns.add_argument('-d', '--datax', help='list of argv data', action='store')
        args_dns.add_argument('-v', '--verbosity', help='print running process', action='store_true')
        args_dns.add_argument('-a', '--all', help='IP for All, set ip address to one ip', action='store')
        args_dns.add_argument('-U', '--update', help='Update/Replace All Host IP, type "update" on HOST option ', action="store", dest='ipaddress')
        args_dns.add_argument('-r', '--remove', help='Remove hostname', action='store_true')
        args_dns.add_argument('-s', '--search', help="Search Configuration of Host", action='store_true')
        #print "len(args) =", len(sys.argv)
        # print "args[-1] =", sys.argv[-1]
        if len(sys.argv) < 4:
            #print "HEH"
            if sys.argv[-1] == "vhost":
                args_vhost.parse_args(['vhost', '-h'])
            elif sys.argv[-1] == "proxy":
                args_proxy.parse_args(['proxy', '-h'])
            elif sys.argv[-1] == "dns":
                args_dns.parse_args(['dns', '-h'])
            elif sys.argv[-1] == "-s":
                args = parser.parse_args()
                self.host_search(args.HOST)            
            parser.print_help()
        
        else:
            #print "len(args) =", len(sys.argv)
            args = parser.parse_args()
            # print "args X =", args
    
            if args.TYPE == "vhost": #Virtual Host (VHOST)
                if args.ip:
                    args.adddns = True
                if args.PATH:
                    if os.path.isdir(args.PATH):
                        self.vhost(args.HOST, args.PATH, args.email, dindex=args.directoryindex, adddns=args.adddns, verbosity=args.verbosity, ipAll=args.ip, passwd_sdns=args.password)
                    elif args.search:
                        self.host_search(args.HOST)
                    else:
                        print "\n"
                        print "\tPlease Insert your PATH !"
                        print "\n"
                        parser.print_help()
                elif args.search:
                    self.host_search(args.HOST)                
                else:
                    if args.delete:
                        self.del_host(args.HOST, args.verbosity)
                        if sys.platform == 'win32':
                            try:
                                c_addhost = addhost.simplednshostadd()
                                c_addhost.del_zone(args.HOST, '127.0.0.1', 8053, 'blackid')
                            except:
                                if args.verbosity:
                                    print traceback.format_exc()
                    elif args.search:
                        self.host_search(args.HOST)                    
                    else:
                        print "\n"
                        print "\tPlease Insert your PATH !"
                        print "\n"
                        parser.print_help()
    
            elif args.TYPE == "proxy": #Proxy
                if args.HOST:
                    if args.delete:
                        self.del_host(args.HOST, args.verbosity)
                    if args.search:
                        self.host_search(args.HOST)                    
                    if args.ip:
                        args.adddns = True
    
                        if args.port:
                            if isinstance(args.port, int):
                                if args.email:
                                    if "@" in args.email:
                                        self.proxy(args.HOST, str(args.port), args.email, args.ip, args.adddns, args.verbosity, args.ip, args.password)
                                    else:
                                        print "\n"
                                        print "\t Please Insert Correct EMAIL !"
                                        print "\n"
                                        parser.print_help()
                                else:
                                    self.proxy(args.HOST, str(args.port), args.email, args.ip, args.adddns, args.verbosity, args.ip, args.password)
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
                        print "\n"
                        print "\tPlease insert IP Address of Proxy HOST !"
                        print "\n"
                        parser.print_help()
                elif args.search:
                    self.host_search(args.HOST)                
                else:
                    print "\n"
                    print "\tPlease insert HOST name !"
                    print "\n"
                    parser.print_help()
    
            elif args.TYPE == 'dns':
                # print "args =", args
                if sys.platform == 'win32':
                    c_addhost = addhost.simplednshostadd()
                    c_addhost.__init__(args.host, args.password, args.port, args.ipA, args.ipNS, args.ipWWW, args.ipMX, args.ipMAIL, args.ipFTP, args.all, args.email, args.HOST, args.verbosity)
                    if str(args.HOST).lower() == "update":
                        c_addhost.updateZone(args.ipaddress)
                    if args.search:
                        self.host_search(args.HOST)                
                    if args.remove:
                        c_addhost.del_zone(args.HOST)
                    if args.all:
                        if str(args.HOST).lower() == "update":
                            c_addhost.updateZone(args.all)
                        else:
                            c_addhost.add(args.HOST, args.port, args.all, args.all, args.all, args.all, args.all, args.all, args.host, args.password, args.email, args.datax, args.verbosity)
                    else:
                        if str(args.HOST).lower() == "update":
                            pass
                        elif args.remove:
                            pass
                        else:
                            if args.ipA == None:
                                args_dns = args_dns.parse_args(['dns', '-h'])
                            else:
                                c_addhost.add(args.host, args.port, args.ipA, args.ipNS, args.ipWWW, args.ipMX, args.ipFTP, args.ipMAIL, args.host, args.password, args.email, args.datax, args.verbosity)
            elif args.search:
                self.host_search(args.HOST)            
            else:
                print "\n"
                print "\tPlase select your TYPE !"
                print "\n"
                parser.print_help()
    
    def split(self, data):
        #print "DATA =", data
        list_updown = []
        config_01 = {}
        d001 = data.split("\n")
        print "\n"
        print "Main Config  :\n"
        for i in d001:
            if "VirtualHost" in i:
                pass
            else:
                #print "i =", i
                d002 = str(i).split("\t")
                #print "len(d002) =",len(d002)
                #print "d002 =", d002
                for a in d002:
                    if a =='':
                        pass
                    else:
                        #print "a =", a
                        b = []
                        k = str(a).split(" ")
                        for t in k:
                            if t != '':
                                b.append(t)
                        if len(b) > 0:
                            if "#" in b[0]:
                                pass
                            #elif len(b) ==1:
                                #pass
                            elif b[0][0] == "<" and b[0][0:2] != "</":
                                index_up   = ''
                                index_down = ''
                                #print "i              =", i
                                #print "b[0][1:4]      =", b[0][1:3]
                                if "if" in str(b[0][1:3]).lower():
                                    b[0] = b[0][3:] + " - " + b[1][0:len(b[1])-1]
                                    config_01.update({b[0]:[]})
                                else:
                                    config_01.update({b[0][1:]:[]})
                                    b[0] = b[0][1:]
                                #print "config_01      =", config_01
                                #print "b              =", b
                                #print "b[0]           =", b[0]
                                #print "d001[index-i]  =", d001[d001.index(i)]
                                #print "d001.index(i)  =", d001.index(i)
                                index_up = d001.index(i) + 1
                                #print "d001[index_up] =", d001[index_up]
                                #print "len(d001)      =", len(d001)
                                for i2 in range(index_up, len(d001)):
                                    if "</" in d001[i2]:
                                        #print "i2             =", i2
                                        #print "d001[i2]       =", d001[i2]
                                        index_down = i2 - 1
                                        #print "i2 - 1         =", i2 - 1
                                                                
                                        #print "index_up       =", index_up
                                        #print "index_down     =", index_down
                                        list_updown.append((b[0], index_up, index_down))
                                        #print "-"*120
                                        break
                            else:
                                if b[0][0] == "<":
                                    pass
                                elif len(b) ==1:
                                    pass                        
                                else:
                                    print "\t" + b[0] + (25 - len(b[0]))*' ' + " =", (" ".join(b[1:])).strip()
                                    
        #print "config"
        #print "list_updown =", list_updown
        for x in list_updown:                            
            #print "x =", x
            for z in range(x[1], x[2] + 1):
                #print d001[z]
                d003 = str(d001[z]).split("\t")
                #print "D003 =", d003
                for y in d003:
                    if y == '':
                        pass
                    else:
                        config_01.get(x[0]).append(y)
                        
        #print "\n"
        #print "config_01 =",config_01
        print "\n"
        print "Sub Config  :\n"
        for i in config_01:
            if len(config_01.get(i)) > 1:
                for a in config_01.get(i):
                    print "\t" + i + (25 - len(i))*' ' + " =", a
            else:
                print "\t" + i + (25 - len(i))*' ' + " =", config_01.get(i)[0]
    
    def host_search(self, search):
        if os.path.isdir(self.getCfg('PATH', 'master')):
            list_host = os.listdir(self.getCfg('PATH', 'master'))
            for i in list_host:
                if str(search).lower() in i:
                    f = open(os.path.join(self.getCfg('PATH', 'master'), i), 'r').read()
                    #print "F =", f
                    self.split(f)
                    #f.close()
                    
        

if __name__ == "__main__":
    vhostmaker = maker()
    vhostmaker.usage()
    #vhostmaker.host_search(sys.argv[1])
