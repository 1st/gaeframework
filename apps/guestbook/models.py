from gae import db
from apps.user import get_current_user

class Message(db.Model):
    author  = db.UserProperty(auto_current_user_add=True)
    content = db.StringProperty(multiline=True, required=True)
    date    = db.DateTimeProperty(auto_now_add=True)
    
    def manager(self):
        '''If user allow to manage current message'''
        current_user = get_current_user()
        return self.author == current_user or current_user.is_admin