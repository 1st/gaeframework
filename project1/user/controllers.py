'''
User account management.
'''
from apps.user.forms import UserLoginForm, UserRegistrationForm
from apps.user.models import User
from apps.user import login_required


def users_list(request):
    return request.render('user/users_list', users = User.all().order("-created"))


def login(request):
    if request.POST:
        # filled form
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            nick = form.cleaned_data.get("nick")
            password = form.cleaned_data.get("password")
            user = User.get_by_key_name(nick)
            # correct user
            if user and user.password == password:
                request.session["user"] = user
                # when the user login, that we rotate the session ID (security)
                request.session.regenerate_id()
                return request.redirect("go back")
            else:
                form._errors["nick"] = form.error_class(["User with given nick name and password not found"])
    else:
        # empty form
        form = UserLoginForm()
    return request.render('user/login', form = form)

@login_required()
def logout(request):
    del request.session["user"]
    return request.redirect("go back")

def registration(request):
    if request.POST:
        # filled form
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            # check user nick name duplicates
            nick = form.cleaned_data.get("nick")
            if User.get_by_key_name(nick):
                form._errors["nick"] = form.error_class(["User with given nick name already registered"])
            else:
                user = form.save()
                request.session["user"] = user
                # when the user login, that we rotate the session ID (security)
                request.session.regenerate_id()
                return request.redirect("go back")
    else:
        # empty form
        form = UserRegistrationForm()
    return request.render('user/registration', form = form)

def activate(request, account_id):
    '''Activate already registered user account'''
    pass

def deactivate(request, account_id):
    '''Deactivate user account'''
    pass
