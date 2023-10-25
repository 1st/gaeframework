from gae import forms
from apps.location.models import Country, Region, City

class CountryCreateForm(forms.ModelForm):
    class Meta:
        model   = Country
#        exclude = ('author',)

    def clean_slug(self):
        '''Prevent duplicate blogs with equal key names'''
        # blog with giwen url address already exists
        if self.Meta.model.get_by_key_name(self.cleaned_data['slug']):
            raise forms.ValidationError("Blog with url '%s' already exists" %
                                         self.cleaned_data['slug'])
        return self.cleaned_data['slug']

