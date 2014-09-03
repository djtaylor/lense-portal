class ScheduleAPI:
    def __init__(self, parent):
        self.parent = parent
       
    def get(self, data=None):
        return self.parent._get(data=data, action='get', path='schedule')