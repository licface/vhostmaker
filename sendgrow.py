from gntplib import Publisher,  Resource
import gntplib
class growl:
    def __init__(self):
        pass
    
    def publish(self, app, event, title, text, host='127.0.0.1', port=30000, timeout=20, icon=None, iconpath=None):
        iconx = Resource(open(iconpath, 'rb').read())
        #publisher = Publisher(app, event, host=host, port=port, timeout=timeout)
        publisher = Publisher(app, [event], timeout=timeout, icon=iconx)
        publisher.register()
        publisher.publish(event, title, text, icon=iconx)
        
    def published(self, app, event, title, text, host='127.0.0.1', port=30000, timeout=120, iconpath=None):
        icon = Resource(open(iconpath, 'rb').read())
        pb = gntplib.Publisher(app, [event], timeout=timeout, icon=icon)
        #publisher = Publisher(app, event, host=host, port=port, timeout=timeout)
        #publisher.register()
        pb.register()
        gntplib.publish(app, event, title, text)
        
    def send(event, title, text):
        gntplib.publish(event, title, text)
        
        
#if __name__ == "__main__":
#    mclass = growl()
#    event = ['test by me']
#    mclass.published('test', event, "Just Test", "HELLLOOOOOOOO", icon=icon)