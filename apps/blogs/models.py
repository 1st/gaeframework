from gae import db
from apps.user import get_current_user

class Blog(db.UniqueModel, db.Model):
    KEY_NAME = "%(slug)s"
    slug = db.StringProperty('blog url', required=True)
    name = db.StringProperty('blog name', required=True)
    author = db.UserProperty(auto_current_user_add=True, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    active = db.BooleanProperty(default=False)

    def __unicode__(self):
        return self.slug

    def manager(self):
        '''If user allow to manage current article'''
        current_user = get_current_user()
        return self.author == current_user or current_user.is_admin
    
    def details_url(self):
        return self.key().name()

    def edit_url(self):
        return "%s/edit" % self.key().name()

    def delete_url(self):
        return "%s/delete" % self.key().name()

class Tag(db.Model):
    slug = db.StringProperty('tag url', required=True)
    name = db.StringProperty('tag name', required=True)
    used = db.IntegerProperty('tag used times', default=0)

    def __unicode__(self):
        return self.name

class Entity(db.UniqueModel, db.Model):
    KEY_NAME = "%(blog)s/%(slug)s"
    slug = db.StringProperty('blog post url', required=True)
    title = db.StringProperty(required=True)
    description = db.StringProperty()
    text = db.TextProperty(required=True)
    author = db.UserProperty(auto_current_user_add=True, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    changed = db.DateTimeProperty(auto_now=True)
    active = db.BooleanProperty(default=False)
    # references
    blog = db.ReferenceProperty(reference_class=Blog, required=True)
#    tags = db.ReferenceListProperty(BlogTag)

    def __unicode__(self):
        return self.title

    def manager(self):
        '''If user allow to manage current article'''
        current_user = get_current_user()
        return self.author == current_user or current_user.is_admin

    def details_url(self):
        return self.key().name()

    def edit_url(self):
        return "%s/edit" % self.key().name()

    def delete_url(self):
        return "%s/delete" % self.key().name()