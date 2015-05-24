
data = """
<VirtualHost *:80>
	ServerAdmin root@docs.requests-cache.net
	DocumentRoot "d:\WWW\docs.requests-cache.net"
	ServerName docs.requests-cache.net
	ServerAlias www.docs.requests-cache.net
	ErrorLog "logs/docs.requests-cache.net-error.log"
	CustomLog "logs/docs.requests-cache.net-access.log" common
	# DirectoryIndex index.html
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
		SSLCertificateFile "d:/WWW/SSLCertificateKeyFile//docs.requests-cache.net.crt"
		SSLCertificateKeyFile  "d:/WWW/SSLCertificateKeyFile//docs.requests-cache.net.key"
		#SSLSessionCache        "shmcb:c:/wamp/bin/apache/Apache2.4.4/logs/ssl_scache(512000)"
		SSLSessionCacheTimeout 600   
		<IfModule mime.c>
		AddType application/x-x509-ca-cert      .crt
		AddType application/x-pkcs7-crl         .crl
	</IfModule>
		SetEnvIf User-Agent ".*MSIE.*" nokeepalive ssl-unclean-shutdown downgrade-1.0 force-response-1.0
		ServerName docs.requests-cache.net
		ServerAlias www.docs.requests-cache.net
		ErrorLog "logs/docs.requests-cache.net.https-error.log"
		CustomLog "logs/docs.requests-cache.net.https-access.log" common
</VirtualHost>
	"""
def split():
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
                    b = str(a).split(" ")
                    #print "b =", b
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
        
        
        
                
    
split()
        

