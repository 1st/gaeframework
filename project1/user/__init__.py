import logging
from gae.sessions import get_current_session
from gae.config import get_config
from apps.user.models import User

def get_current_user():
    '''Return current user; otherwise return unautorized user object'''
    session = get_current_session()
    if "user" not in session:
        return None # TODO: return anonymous User() object
    return session['user']

def get_login_url(previous_page):
    '''Return url for user login'''
    return "/user/login?previous_page=%s" % previous_page

def get_logout_url(previous_page):
    '''Return url for user logout'''
    return "/user/logout?previous_page=%s" % previous_page

def login_required(*roles):
    '''
    Decorator for logged users only.

    Args:
        roles - list of roles for users who have access to given request handler
    '''
    def wrap(handler_method):
        def check_login(request, *args, **kwargs):
            user = get_current_user()
            # not logged
            if not user:
                return request.redirect(get_login_url(request.request.path))
            # roles not specified
            if not roles:
                return handler_method(request, *args, **kwargs)
            # check role
            for role in roles:
                # allow access with given role
                if user.has_role(role):
                    return handler_method(request, *args, **kwargs)
            # access denied
            raise request.ACCESS_DENIED
        return check_login
    return wrap
