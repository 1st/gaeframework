from gae import db
from apps.user import get_current_user

class Todo(db.Model):
    author           = db.UserProperty(auto_current_user_add=True, required=True)
    title            = db.StringProperty(required=True)
    description      = db.StringProperty(multiline=True)
    url              = db.StringProperty()
    created          = db.DateTimeProperty(auto_now_add=True)
    updated          = db.DateTimeProperty(auto_now=True)
    due_date         = db.StringProperty(required=True)
    finished         = db.BooleanProperty(default=False)

    def manager(self):
        '''If user allow to manage current todo'''
        current_user = get_current_user()
        return self.author == current_user or current_user.is_admin