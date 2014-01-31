import portalocker
import configparser

cfg = ConfigParser.RawConfigParser()
cfg.read(self.FILECONF)
fd = open(cfg.get('PATH','MASTER'),'r+')
portalocker.unlock(fd)
print fd.readlines()