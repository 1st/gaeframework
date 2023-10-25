import sys, os
import django.template, django.template.loader, django.conf
from gae.template.tag_elif import *
from gae.config import get_config

try:
    # configure django templates loader
    debug = os.environ['SERVER_SOFTWARE'].startswith('Development')
    django.conf.settings.configure(
        DEBUG = debug,
        TEMPLATE_DEBUG = debug,
        TEMPLATE_LOADERS=('gae.template.loader.Loader', 'django.template.loaders.filesystem.load_template_source',),
        LANGUAGE_CODE = get_config("site.language"),
        USE_I18N = True,
        USE_L10N = True,
    )
except (EnvironmentError, RuntimeError), e:
    pass

def render(template_path, template_dict, debug=False):
    """
    Renders the template at the given path with the given dict of values.
    
    Example usage:
      render("app_name/index.html", {"name": "Bret", "values": [1, 2, 3]})
    
    Args:
      template_path: path to a Django template
      template_dict: dictionary of values to apply to the template
    """
    t = load(template_path, debug)
    return t.render(Context(template_dict))


template_cache = {}
def load(path, debug=False):
    """
    Loads the Django template from the given path.
    
    It is better to use this function than to construct a Template using the
    class below because Django requires you to load the template with a method
    if you want imports and extends to work in the template.
    """
    if not debug:
        template = template_cache.get(path, None)
    else:
        template = None
    
    if not template:
        template = django.template.loader.get_template(path)
        if not debug:
            template_cache[path] = template
    
    return template

def create_template_register():
    """Used to extend the Django template library with custom filters and tags.
    
    To extend the template library with a custom filter module, create a Python
    module, and create a module-level variable named "register", and register
    all custom filters to it as described at
    http://www.djangoproject.com/documentation/templates_python/
      #extending-the-template-system:
    
      templatefilters.py
      ==================
      register = webapp.template.create_template_register()
    
      def cut(value, arg):
        return value.replace(arg, '')
      register.filter(cut)
    
    Then, register the custom template module with the register_template_library
    function below in your application module:
    
      myapp.py
      ========
      webapp.template.register_template_library('templatefilters')
    """
    return django.template.Library()


def register_template_library(package_name):
    """Registers a template extension module to make it usable in templates.
    
    See the documentation for create_template_register for more information."""
    if not django.template.libraries.get(package_name, None):
        django.template.add_to_builtins(package_name)


Template = django.template.Template
Context = django.template.Context