from gae import db
from apps.user import get_current_user

class Comment(db.Model):
#    """
#    A user comment about some object.
#    """
    # user info
    author      = db.UserProperty(auto_current_user_add=True)
#    user_name   = db.StringProperty()
#    user_email  = db.EmailProperty()
#    user_site   = db.LinkProperty()
#    user_ip     = db.StringProperty(required=True)
    # comment info
    title       = db.StringProperty(default="Title", required=True)
    text        = db.TextProperty("message", default="Your message", required=True)
    created     = db.DateTimeProperty(auto_now_add=True)
    active      = db.BooleanProperty(default=False)
    # references
    obj         = db.ReferenceProperty(required=False)
#    comment     = db.SelfReferenceProperty("parent comment", collection_name="comments")

    def __unicode__(self):
        return self.title

    def manager(self):
        '''If user allow to manage current comment'''
        current_user = get_current_user()
        return self.author == current_user or current_user.is_admin
