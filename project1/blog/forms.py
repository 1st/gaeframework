from gae import forms
from apps.blog.models import Entity, Tag

class EntityForm(forms.ModelForm):
    tags = forms.CharField(max_length=100, min_length=3, required=False)

    def clean_slug(self):
        '''Prevent duplicate entries with equal key names'''
        # entry with given url address already exists
        entry_key = self.cleaned_data['slug']
        if self.Meta.model.get_by_key_name(entry_key):
            raise forms.ValidationError("Entity with url '%s' already exists" %
                                         self.cleaned_data['slug'])
        return self.cleaned_data['slug']

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', "").strip(" ").lower()
        if tags:
            tags = [tag.strip(" ") for tag in tags.split(",")]
            return [tag for tag in tags if len(tag) > 2]
        return []


class EntityCreateForm(EntityForm):
    class Meta:
        model   = Entity
        exclude = ('author',)


class EntityEditForm(EntityForm):
    class Meta:
        model   = Entity
        exclude = ('author', 'slug')