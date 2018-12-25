from lyrebird import application
from lyrebird.mock import context

class NoticeCenter():
    
    def __init__(self):
        # display notice in frontend
        print('NoticeCenter OnCreate')
        application.server['event'].subscribe('notice', self.display_notice)

    def display_notice(self, msg):
        """
        display notice
        
        """
        context.application.socket_io.emit('show', msg, namespace='/alert')
