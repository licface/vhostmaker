#import ConfigParser

#config = ConfigParser.RawConfigParser()
#cfg = ConfigParser.SafeConfigParser()
#cfg.read('example.cfg')
#cfg.set('Section1','baz','ETETR')
#with open('example.cfg', 'wb') as configfile:
    #cfg.write(configfile)
    
    
#config = ConfigParser.RawConfigParser()
#config.read('example.cfg')
#print config.get('Section1','baz')

#print dir(cfg)

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
#config.add_section('Section1')
#config.set('Section1', 'an_int', '15')
#config.set('Section1', 'a_bool', 'true')
#config.set('Section1', 'a_float', '3.1415')
#config.set('Section1', 'baz', 'fun')
#config.set('Section1', 'bar', 'Python')
#config.set('Section1', 'foo', '%(bar)s is %(baz)s!')

# Writing our configuration file to 'example.cfg'
#with open('example.cfg', 'wb') as configfile:
#    config.write(configfile)

import test

class testyou(test.testme):
	def __init__(self):
		super(testyou)
	
	def test002(self):
		self.test001()

c = testyou()
c.test002()
