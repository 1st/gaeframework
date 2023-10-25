from gae import forms
from apps.todo.models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model   = Todo
        exclude = ['author']