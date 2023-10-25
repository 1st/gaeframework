from gae import db

class Message(db.Model):
    created     = db.DateTimeProperty(auto_now_add=True)
    title       = db.StringProperty(max_length=250, required=True)
    text        = db.TextProperty(required=True)
    email       = db.EmailProperty()

class DirectMessage(Message):
    from_user   = db.UserProperty(auto_current_user_add=True, required=True)
    to_user     = db.UserProperty(required=True)

class Feedback(Message):
    SUBJECTS = ((0, "Other"),
                (1, "I have problems with site"),
                (2, "How it works?"),
                (3, "Advertising"),
                (4, "Investment"))
    subject     = db.StringProperty(choices=SUBJECTS, required=True)