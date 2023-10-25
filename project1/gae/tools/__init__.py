import os, re
from gae.exceptions import IncorrectUrlDefinition

_installed_apps = None
def installed_apps():
    '''
    Return list of installed applications.
    '''
    global _installed_apps
    if not _installed_apps:
        _installed_apps = [app for app in os.listdir('apps') if os.path.isdir(os.path.join('apps', app)) and not app.startswith("_")]
    return _installed_apps

def monkey_patch(name, bases, namespace):
    assert len(bases) == 1, 'Exactly one base class is required'
    base = bases[0]
    for name, value in namespace.iteritems():
        if name not in ('__metaclass__', '__module__'):
            setattr(base, name, value)
    return base

def prepare_url_vars(url_address, template):
    '''
    Return url address with replaced variables to regex pattern.
    
    Examples:
        blog/(blog_slug)/new -> blog/%(blog_slug)s/new
        blog/category-(category_id:number) -> blog/category:(?P<category_slug>[0-9]+)
    '''
    placeholder_types = {
        'string': '[^/]+',
        'all':    '.+',
        'key':    '\w{32}',
        'number': '[0-9]+',
    }
    
    def prepare_url_variable(var_name, var_type):
        if var_type is None: var_type = 'string'
        if "," in var_type: # list of values
            var_type_regex = "(%s)" % "|".join([re.escape(str.strip()) for str in var_type.split(',')])
        else:
            var_type_regex = placeholder_types.get(var_type)
            if var_type_regex is None:
                raise IncorrectUrlDefinition("Url mapping rule has incorrect placeholder type %r" % var_type)
        try:
            return template % (var_name, var_type_regex)
        except TypeError:
            return template % var_name
    
    result = re.sub("\(([a-z][a-z0-9_]*)(:([a-z, ]+))?\)", lambda x: prepare_url_variable(x.group(1), x.group(3)), url_address).replace(" ", "")
    return result
