'''
All available exceptions in GAE framework engine.
'''

class AccessDenied(Exception):
    '''403 error'''
    pass

class PageNotFound(Exception):
    '''404 error'''
    pass

class Redirect(Exception):
    '''Redirect user to another page'''
    def __init__(self, destintion, permanent=False):
        self.destintion = destintion
        self.permanent = permanent
    
    def __str__(self):
        return self.destintion
        

class IncorrectUrlDefinition(Exception):
    '''Incorrect url'''
    pass