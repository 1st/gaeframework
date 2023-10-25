from gae import db

class Tag(db.Model):
    name = db.StringProperty('tag name', required=True)
    used = db.IntegerProperty('tag used times', default=0)

    def __unicode__(self):
        return self.name

class Entity(db.UniqueModel, db.Model):
    KEY_NAME = "%(slug)s"
    slug = db.StringProperty('entry url', required=True)
    title = db.StringProperty(required=True)
    description = db.StringProperty()
    text = db.TextProperty(required=True)
    author = db.UserProperty(auto_current_user_add=True, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    changed = db.DateTimeProperty(auto_now=True)
    active = db.BooleanProperty(default=False)
    tags = db.StringListProperty()

    def __unicode__(self):
        return self.title