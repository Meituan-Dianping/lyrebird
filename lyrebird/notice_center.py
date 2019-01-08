from lyrebird import application
from lyrebird.mock import context

class NoticeCenter():
    
    def __init__(self):
        # display notice in frontend
        application.server['event'].subscribe('notice', self.push_notice)

    def push_notice(self, msg):
        """
        display notice
        
        """
        context.application.socket_io.emit('show', msg)
