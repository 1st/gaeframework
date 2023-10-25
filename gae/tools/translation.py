import yaml, logging
from gae.config import get_config

__all__ = ["translate", "_", "get_language", "get_available_languages", "set_language"]

_language = None

def get_language():
    '''eturn current active language'''
    global _language
    # language is not defined - load from config
    if not _language:
        _language = get_config('site.language', 'en')
    return _language

def get_available_languages():
    '''Return list of available site translations'''
    return get_config("site.languages", [])

def set_language(language):
    '''Activate current language'''
    global _language
    # use only supported language
    if language in get_available_languages():
        _language = language

class LazyTranslate:
    _translations = {}
    msg = None
    app = None

    def __init__(self, msg, app_name=None):
        self.msg = unicode(msg)
        self.app = app_name

    def __str__(self):
        return self.translate(self.msg, self.app)

    def __unicode__(self):
        return self.__str__()#.encode('utf-8')

    def __repr__(self):
        return "<%s instance of %r>" % (self.__class__.__name__, self.msg)

    @staticmethod
    def translate(message, app_name):
        '''Return translated message from Englist to current language from given application'''
        language = get_language()
        if language not in LazyTranslate._translations:
            LazyTranslate._translations[language] = {}
        # load translation for specified application
        if app_name not in LazyTranslate._translations[language]:
            file = "%s/translate/%s.yaml" % (app_name, language)
            LazyTranslate._translations[language][app_name] = LazyTranslate.load_translation(file)
        # translate message in specified application
        if message in LazyTranslate._translations[language][app_name]:
            return LazyTranslate._translations[language][app_name][message]
        # load global site translation
        if "site" not in LazyTranslate._translations[language]:
            file = "%s/translate/%s.yaml" % ("site", language)
            LazyTranslate._translations[language]["site"] = LazyTranslate.load_translation(file)
        # translate message with global translation
        if message in LazyTranslate._translations[language]["site"]:
            return LazyTranslate._translations[language]["site"][message]
        # translation not found - return original English message
        return message

    @staticmethod
    def load_translation(path):
        '''Load translation file and return the dictionary'''
        translations = {}
        try:
            fd = open(path)
            # if file is empty - we create an empty dictionary
            translations = yaml.load(fd) or {}
            fd.close()
            logging.info("Translation '%s' was loaded" % path)
        except:
            translations = {}
            logging.warning("Translation '%s' not loaded" % path)
        return translations

def translate(message, app_name=None):
    return LazyTranslate(message, app_name)

# short form
_ = translate