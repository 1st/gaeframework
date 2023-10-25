from django.template.loader import render_to_string
from gae import template
from gae.tags import node_rule, BaseNode
from apps.user.forms import UserLoginForm, UserRegistrationForm

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ("",))
def login_form(self, context):
    """Render the user login form"""
    form = UserLoginForm()
    return render_to_string("user/login_form",
                            {'form': form},
                            context_instance = context)

@register.tag
@node_rule(BaseNode, ("",))
def registration_form(self, context):
    """Render the user registration form"""
    form = UserRegistrationForm()
    return render_to_string("user/registration_form",
                            {'form': form},
                            context_instance = context)
