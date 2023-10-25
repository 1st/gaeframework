import os, sys, urllib, re, logging, webob, urlparse, traceback
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.appstats import recording
from google.appengine.ext import db
from google.appengine.api.app_identity import get_application_id
from django.conf import settings as django_settings
from django.utils import simplejson
from gae.sessions import SessionMiddleware, get_current_session
from gae.config import get_config
from gae.tools import prepare_url_vars, installed_apps
from gae.exceptions import AccessDenied, PageNotFound, Redirect, IncorrectUrlDefinition
from gae import template
from apps.user import get_current_user


class Content:
    '''
    Contains data in not handled format.
    Allowed JSON, XML and HTML formats (not rendered page).
    '''
    data = None
    mime_type = None
    template = None

    def __init__(self, data, template=None, mime_type=None):
        self.data = data
        self.mime_type = mime_type and mime_type.lower()
        self.template = template

    def __unicode__(self):
        if self.template:
            return template.render(self.template, self.data, WSGIApplication.debug)
        elif self.mime_type == "json":
            return simplejson.dumps(self.data)
        elif self.mime_type == "xml":
            raise NotImplemented
        return self.data

#    def __str__(self):
#        return self.__unicode__().encode('utf8')


class Request(webapp.Request):
    '''
    User request with an real environment with a POST and GET dicts,
    SESSION and USER objects and additional tools to use around the
    controllers.
    
    Used for call controller (request handler) and return result.
    '''
    ACCESS_DENIED = AccessDenied
    PAGE_NOT_FOUND = PageNotFound
    REDIRECT = Redirect

    def __init__(self, environ, debug):
        self.__debug = debug
        super(Request, self).__init__(environ)

    def run_controller(self, app_name, controller_name, **params):
        '''
        Load application and run controller.
        
        Result send to user.
        '''
        module = __import__("apps.%s.controllers" % app_name, {}, {}, ["controllers"])
        controller = getattr(module, controller_name)
        return controller(self, **params)

    @property
    def user(self):
        '''Return active user object.
        If not authorized - return None'''
        return get_current_user()

    @property
    def session(self):
        '''Return user session'''
        return get_current_session()

    def log(self, message, flagged='info'):
        '''Save logging message'''
        if flagged in ("warn", "warning"):
            logging.warning(message)
        elif flagged in ("err", "error"):
            logging.error(message)
        elif flagged == "debug":
            logging.debug(message)
        else:
            logging.info(message)

    def redirect(self, to_page, permanent=False):
        '''Redirect user to given page'''
        # human-readable shortcuts
        if to_page in ["go back", "back"]:
            to_page = self.previous_page
        elif to_page in ["reload", "reload page", "refresh", "refresh page"]:
            to_page = self.path
        to_page = to_page.encode("utf-8")
        raise self.REDIRECT(to_page, permanent)

    @property
    def previous_page(self):
        '''Return previous page address'''
        # passed "previous_page" - link to previous page
        if self.get('previous_page'):
            return self.get('previous_page')
        # link to previous page
        elif 'HTTP_REFERER' in os.environ and os.environ['HTTP_REFERER'].startswith("http://%s/" % self.host):
            return re.split('^https?://[^/]+', os.environ['HTTP_REFERER'])[1]
        # current page
        return self.path

    def render(self, template_name, **variables):
        '''Render given template with a given variables dict'''
        # add file extension
        template_name += '.html'
        # set predefined values to template
#        variables['app'] = self.app_name
        variables['request'] = self
        variables['user'] = self.user
        variables['session'] = self.session
        variables['previous_page'] = self.previous_page
        variables['current_page'] = self.path
        # load template from global templates
        return Content(variables, template_name)

    def json(self, **variables):
        '''Convert variables dict to JSON representation'''
        return Content(variables, mime_type="json")

    def xml(self, **variables):
        '''Convert variables dict to XML representation'''
        return Content(variables, mime_type="xml")

    @property
    def is_ajax(self):
        '''Return True if given request initialized via AJAX call'''
        return self.is_xhr

    @property
    def installed_apps(self):
        return installed_apps()

#    def handle_exception(self, exception):
#        """
#        Called if this handler throws an exception during execution.
#        
#        Args:
#          exception: the exception that was thrown
#        """
#        # show error page for user
#        if not self.__debug:
#            if self.status_code is not None and int(self.status_code) != 200:
#                return self.render("site/%s" % self.status_code)
#            return None
#        # show detailed error traceback
#        try:
#            errors = {"request": self,
#                      "error": "%s: %s" % (sys.exc_info()[0].__name__, sys.exc_info()[1]),
#                      "status_code": self.status_code,
#                      "traceback": self._traceback_info()}
#            # render page with status code on errors
#            return self.render("site/debug", errors)
#        except TypeError, e:
#            logging.warning("Template '%s' not found" % e)
#        except (TypeError, Exception), e:
#            logging.warning(e)
#        # print raw traceback (without insert to 500 template)
#        errors_html = ""
#        for error_name, error_details in errors.items():
#            if type(error_details) in (tuple, dict, list):
#                errors = []
#                for frame, vars in error_details:
#                    errors.append("%s\n%s" % (
#                                  "%s (line %s) in %s" % (frame['func'], frame['line'], frame['file']),
#                                  "\n".join(["  %s = %s" % (var_name, var_repr) for var_name, var_repr, var_value in vars])))
#                error_details = "\n".join(errors)
#            errors_html += "<div class='%(error_name)s'>"\
#                "<h2>%(error_name)s</h2>"\
#                "<pre>%(error_details)s</pre>"\
#                "</div>" % {
#                    "error_name": error_name.title(),
#                    "error_details": error_details}
#        # return error page
#        return "<html><body>%s</html></body>" % errors_html

#    def _traceback_info(self):
#        """
#        Print the usual traceback information, followed by a listing of all the
#        local variables in each frame.
#        """
#        tb = sys.exc_info()[2]
#        while 1:
#            if not tb.tb_next: break
#            tb = tb.tb_next
#        stack = []
#        f = tb.tb_frame
#        while f:
#            stack.append(f)
#            f = f.f_back
#        frames = []
#        for frame in stack:
#            vars = []
#            for key, value in frame.f_locals.items():
#                if key.startswith("__"): continue # not show special variables
#                #We have to be careful not to cause a new error in our error
#                #printer! Calling str() on an unknown object could cause an
#                #error we don't want.
#                try:
#                    var_repr = repr(value)
#                    var_value = unicode(value)
#                    vars.append((key, var_repr, var_value if value != var_value and var_value != var_repr else None))
#                except:
#                    pass
#            frame_info = {"func": frame.f_code.co_name, "file": frame.f_code.co_filename, "line": frame.f_lineno}
#            frames.append((frame_info, vars))
#        return frames


class WSGIApplication(webapp.WSGIApplication):
    REQUEST_CLASS = Request
    _urls = []
    _project_dir = None
    active_instance = None
    debug = property(lambda self: self.__debug)
    
    def __init__(self, project_dir, debug=False):
        self.__debug = debug
        self.current_request_args = ()
        self._project_dir = project_dir
        # TODO: if urls have errors than traceback printed on live server
        self.load_urls()
        self.load_models()
        self.prepare_template_engine()
        WSGIApplication.active_instance = self
        
    
    def __call__(self, environ, start_response):
        """
        Called by WSGI when a request comes in.
        """
        request = self.REQUEST_CLASS(environ, self.__debug)
        response = self.RESPONSE_CLASS()
        WSGIApplication.active_instance = self
        
        # search url address
        url_address = request.path.strip('/') + "/"
        url_address = urllib.unquote(url_address).decode("utf-8")
        url_params = None
        for rule in self._urls:
            match = re.match(rule['compiled_url'], url_address)
            # if url found
            if match:
                url_params = 'arg' in rule and rule['arg'] or {}
                # add matched parameters from url string
                url_params.update(match.groupdict())
                break
        if url_params is None:
            response.set_status(404)
        elif 'run' not in rule:
            logging.error("Not defined 'run' argument in urls mapping. Rule: %r" % rule)
            response.set_status(404)
        else:
            # decode url string parameters
            for name, value in url_params.items():
                url_params[name] = urllib.unquote(value)
                if type(url_params[name]) is not unicode: # encode url parameters
                    url_params[name] = url_params[name].decode("utf-8")
            # run application handler
            (app_name, app_controller) = rule['run'].split('.', 1)
            try:
                result = request.run_controller(app_name, app_controller, **url_params)
            except Request.REDIRECT, err:
                uri, permanent = err.destintion, err.permanent
                response.set_status(permanent and 301 or 302)
                absolute_url = urlparse.urljoin(request.uri, uri)
                response.headers['Location'] = str(absolute_url)
                response.clear()
            except Request.ACCESS_DENIED:
                response.set_status(403)
                response.clear()
            except Request.PAGE_NOT_FOUND:
                response.set_status(404)
                response.clear()
            except:
                response.set_status(500)
                response.clear()
                traceback_message = ''.join(traceback.format_exception(*sys.exc_info()))
                if self.__debug:
                    response.out.write("<pre>%s</pre>" % traceback_message)
                else:
                    logging.error("Run %s.%s" % (app_name, app_controller))
                    logging.error(traceback_message)
            else:
                response.out.write(unicode(result))

        response.wsgi_write(start_response)
        return ['']
    
    @staticmethod
    def load_models():
        '''
        Load models from all installed applications.
        
        This is need to resolve conflict with references between
        some models placed in different applications.
        '''
        flag_name = "gae_models_loaded"
        if flag_name in db._kind_map:
            return False
        for app_name in installed_apps():
            try:
                app_models = __import__("apps.%s.models" % app_name, {}, {}, ["models"])
            except ImportError, e:
                logging.warning("File 'apps/%s/models.py' not loaded. %s" % (app_name, e))
                continue
            models = [getattr(app_models, model_name) for model_name in dir(app_models) if not model_name.startswith("_") and model_name[0].isupper()]
            for model in models:
                db._kind_map[model.kind()] = model
        db._kind_map[flag_name] = True

    def load_urls(self):
        '''
        Load urls mapping and cache it for the future requests.
        '''
        if self._urls:
            return False
        # load urls mapping
        self._urls = self._map_urls('site')
        try: # compile regular expressions
            for rule in self._urls:
                rule['compiled_url'] = re.compile("%s" % rule['url'])
        except Exception, err:
            logging.error("Error in urls mapping (rule %r). Error: %s" % (rule['url'], err))
            self._urls = []
        return True

    def _map_urls(self, app_name, parent_rule={}):
        urls = []
        if app_name not in installed_apps():
            raise Exception("Application %s is not available" % app_name)
        for rule in get_config('%s.urls' % app_name, {}):
            if "url" not in rule:
                raise Exception("Not defined 'url' argument in the urls mapping for application '%s'. Rule: %r" % (app_name, rule))
            if "run" not in rule:
                raise Exception("Not defined 'run' argument in the urls mapping for application '%s'. Rule: %r" % (app_name, rule))
            
            if rule["run"].count('.') == 1: # run: app.controller
                try:
                    rule['url'] = self._prepare_url(rule['url'], parent_rule.get('url'))
                except IncorrectUrlDefinition, e:
                    raise IncorrectUrlDefinition("Url rule %r in app %s is incorrect. Error: %s" % (rule, app_name, e))
                urls.append(rule)
            elif rule["run"].count('.') == 0: # run: app
                urls.extend(self._map_urls(rule["run"], rule))
            else: # run: app.controller.whatever
                raise Exception("Incorrect definition of 'run' argument in the urls mapping for application '%s'. Rule: %r" % (app_name, rule))
        return urls

    def _prepare_url(self, url, url_prefix=""):
        '''Return url rule to use in regular expressions module'''
        # compatibility for use empty string in url (without manually setting empty string as "")
        if url is None: url = ""
        if url_prefix is None: url_prefix = ""
        # delete trailing spaces
        url = url.strip('/')
        url_prefix = url_prefix.strip('/')
        # replace '[var_name]' and '[varname:type]' to regular expression rule
        url = prepare_url_vars(url, "(?P<%s>%s)")
        url_prefix = prepare_url_vars(url_prefix, "(?P<%s>%s)")
        # delete spaces after join url with prefix, if url or prefix is empty
        return "^%s/?$" % "/".join([url_prefix, url]).strip('/')

    def prepare_template_engine(self):
        # load template tags and set global template directory
        if not django_settings.TEMPLATE_DIRS:
            django_settings.TEMPLATE_DIRS = (os.path.join(self._project_dir, 'templates'), )
            # use patched and additional template tags
            template.register_template_library('gae.tags')
            # register template tags for each  application
            for app_name in installed_apps():
                try:
                    mod = __import__("apps.%s.tags" % app_name, globals(), {}, app_name)
                    template.django.template.libraries[app_name] = mod.register
                except ImportError:
                    pass


def run(project_dir, appstats=True, debug=None):
    # auto detect environment (development or production)
    if debug is None:
        debug = os.environ['SERVER_SOFTWARE'].startswith('Development')
    COOKIE_KEY = 'my_private_key_used_for_this_application_%s' % get_application_id()
    app = WSGIApplication.active_instance or WSGIApplication(project_dir, debug)
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY, cookie_only_threshold=0)
    if appstats:
        app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)
