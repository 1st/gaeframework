from gae import forms
from apps.blogs.models import Blog, Entity

class BlogCreateForm(forms.ModelForm):
    class Meta:
        model   = Blog
        exclude = ('author',)

    def clean_slug(self):
        '''Prevent duplicate blogs with equal key names'''
        # blog with given url address already exists
        if self.Meta.model.get_by_key_name(self.cleaned_data['slug']):
            raise forms.ValidationError("Blog with url '%s' already exists" %
                                         self.cleaned_data['slug'])
        return self.cleaned_data['slug']

class BlogEditForm(forms.ModelForm):
    class Meta:
        model   = Blog
        exclude = ('author', 'slug')

    def clean_slug(self):
        '''Prevent duplicate blogs with equal key names'''
        # blog with given url address already exists
        if self.Meta.model.get_by_key_name(self.cleaned_data['slug']):
            raise forms.ValidationError("Blog with url '%s' already exists" %
                                         self.cleaned_data['slug'])
        return self.cleaned_data['slug']

class EntityCreateForm(forms.ModelForm):
    class Meta:
        model   = Entity
        exclude = ['author', 'blog']

    def clean_slug(self):
        '''Prevent duplicate entities with equal key names'''
        # entity with given url address already exists
        entity_key = "%s/%s" % (self.initial['blog'].key().name(), self.cleaned_data['slug'])
        if self.Meta.model.get_by_key_name(entity_key):
            raise forms.ValidationError("Blog entity with url '%s' already exists" %
                                         self.cleaned_data['slug'])
        return self.cleaned_data['slug']

class EntityEditForm(forms.ModelForm):
    class Meta:
        model   = Entity
        exclude = ['author', 'blog', 'slug']

    def clean_slug(self):
        '''Prevent duplicate entities with equal key names'''
        # entity with given url address already exists
        entity_key = "%s/%s" % (self.instance.blog.key().name(), self.cleaned_data['slug'])
        if self.Meta.model.get_by_key_name(entity_key):
            raise forms.ValidationError("Blog entity with url '%s' already exists" %
                                         self.cleaned_data['slug'])
        return self.cleaned_data['slug']