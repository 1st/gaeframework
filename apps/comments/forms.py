from gae import forms
from apps.comments.models import Comment

class CommentAdminForm(forms.ModelForm):
    class Meta:
        model   = Comment
        exclude = ['author', 'user_name', 'user_email', 'user_site', 'user_ip', 'active', 'obj', 'comment']

class CommentInlineAdminForm(forms.ModelForm):
    class Meta:
        model   = Comment
        exclude = ['author', 'user_name', 'user_email', 'user_site', 'user_ip', 'active', 'obj', 'comment']

class UserCommentForm(forms.ModelForm):
    obj = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model   = Comment
        exclude = ['author', 'user_name', 'user_email', 'user_site', 'user_ip', 'active', 'obj', 'comment']

class GuestCommentForm(forms.ModelForm):
    class Meta:
        model   = Comment
        exclude = ['author', 'user_ip', 'status', 'obj', 'comment']
