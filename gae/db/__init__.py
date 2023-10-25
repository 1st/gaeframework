import os, logging
from google.appengine.api import memcache
from google.appengine.ext.db import *
from gae.tools import monkey_patch


class Model(Model):
    '''
    Base model class with additional features:
     - adds application name to model class name
     - allow compare two model instances by the key
    '''
    @classmethod
    def kind(cls):
        '''Return class name in format <AppnameClassname>'''
        # get application name from path "app_name.models"
        app_name = cls.__module__.split('.')[1].title()
        # application name and model name have the same name like BlogBlog
        if app_name.lower() == cls.__name__.lower():
            return cls.__name__
        # add application name as prefix of model
        return "%s%s" % (app_name, cls.__name__)

    def __eq__(self, other):
        # compare objects keys
        if self.is_saved() and isinstance(other, Model) and other.is_saved():
            return self.key() == other.key()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class UniqueModel:
    '''Model with control unique properties'''
    
    def put(self, **kwargs):
#        if not self.is_saved():
#            self._key_name = self._generate_key()
        self._key_name = self._generate_key()
        super(Model, self).put(**kwargs)

    def _generate_key(self):
        """A Model for entities which automatically generate their own key names
        on creation."""
        key_name = None
        if hasattr(self, 'KEY_NAME'):
            # get value for each property
            properties = dict()
            for prop in self.properties().values():
                value = getattr(self, prop.name)
                if hasattr(value, 'key'):
                    value = value.key().name()
                properties[prop.name] = value 
            # The KEY_NAME must either be a callable or a string.
            # If it's a callable,we call it with the given keyword args.
            if callable(self.KEY_NAME):
                key_name = self.KEY_NAME(properties)
            # If it's a string, we just interpolate the keyword args into the
            # string, ensuring that this results in a different string.
            else:
                # Try to create the key name, catching any key errors arising
                # from the string interpolation
                try:
                    key_name = str(self.KEY_NAME) % properties
                except KeyError:
                    raise RuntimeError, "Missing keys required by %s entity's "\
                                        "KEY_NAME property (got %r)" %\
                                        (self.entity_type(), properties)
                # Make sure the generated key name is actually different from
                # the template
                if key_name == str(self.KEY_NAME):
                    raise RuntimeError, 'Key name generated for %s entity is '\
                                        'same as KEY_NAME template' %\
                                        self.entity_type()
        # return changed arguments
        return key_name


class CachedModel:
    '''Model with cache support for properties'''
    MEMCACHE_LIFETIME = 3600 # in seconds

    def __getattr__(self, name):
        '''
        Return cached property.

        Usage: blog_entry.author__nick'''
        try:
            # check parent class virtual property
            return super(Model, self).__getattr__(name)
        except AttributeError:
            pass
        if name.find("__") <= 0: # not handle "__iter__" and other magic methods
            raise AttributeError
        # try to load cached property
        memcache_key = "Kind: %s. Key: %s. Property: %s" % (self.kind(), self.key(), name)
        # load field from memcache
        field_value = memcache.get(memcache_key)
        if field_value is None:
            try:
                # get field value based on sequence of field names
                field_value = self
                for field in name.split('__'):
                    if field_value is None: break
                    field_value = getattr(field_value, field)
                    # call method
                    if callable(field_value):
                        field_value = field_value()
                # convert value to string
                if isinstance(field_value, (Model, Property)):
                    field_value = unicode(field_value)
            except:
                raise AttributeError
            if field_value is not None: # set field value to memcache
                if not memcache.add(memcache_key, field_value, time=self.MEMCACHE_LIFETIME):
                    logging.error("Memcache set failed. CachedModel field %r" % name)
        return field_value

class Property(Property):
    __metaclass__ = monkey_patch

    def validate(self, value):
        '''
        Fixed: for attribute [String]ListProperty used choices parameter,
               Validation is incorrect, because compared list value with each
               value in choices.
        '''
        if self.empty(value):
            if self.required:
                raise BadValueError('Property %s is required' % self.name)
        else:
            if self.choices:
                import types
                match = False
                if type(value) in (types.ListType, types.TupleType):
                    # delete duplicates
                    value = list(set(value))
                    # all values is in choices
                    if not list(set(value).difference(set(self.choices))):
                        match = True
                else:
                    # one value is is choices
                    if value in self.choices:
                        match = True
                if not match:
                    raise BadValueError('Property1 %s is %r; must be one of %r' %
                                           (self.name, value, self.choices))
        if self.validator is not None:
            self.validator(value)
        return value


class PhoneListProperty(StringListProperty):
    max_length = 10
    min_length = 5

    def validate(self, value):
        value = super(ListProperty, self).validate(value)
        if value is not None:
            # check each phone
            for item in value:
                if len(item) > self.max_length or len(item) < self.min_length:
                    raise BadValueError(
                        'Phone number %s is incorrect. Enter number in format (xxx) xx-xx-xxx' %
                        (item,))
        return value

    def get_form_field(self, **kwargs):
        defaults = {'initial': ""}
        defaults.update(kwargs)
        return super(StringListProperty, self).get_form_field(**defaults)

    def get_value_for_form(self, instance):
        value = super(PhoneListProperty, self).get_value_for_form(instance)
        if not value:
            value = "---"
        if isinstance(value, basestring) and len(value)>0:
            value = value.splitlines()
        if isinstance(value, list):
            value = ', '.join(value)
        return value

    def make_value_from_form(self, value):
        import re
        if not value:
            return []
        if isinstance(value, basestring):
            # delete all not numbers
            value = [re.sub('[^0-9]', '', phone) for phone in value.split(',')]
        return value


class ReferenceListProperty(ListProperty):
    def __init__(self, reference_type, verbose_name=None, default=None, **kwds):
        self.reference_type = reference_type
        super(ReferenceListProperty, self).__init__(item_type=Key,
                                                verbose_name=verbose_name,
                                                default=default,
                                                **kwds)


class ImageProperty(UnindexedProperty):
    """Image blob"""

    data_type  = Blob
    min_width  = None
    min_height = None
    max_width  = None
    max_height = None
    max_size   = None

    def __init__(self, verbose_name=None, min_width=None, min_height=None,
                 max_width=None, max_height=None, max_size=None, **kwds):
        """
        Construct image property.
    
        Args:
          verbose_name: Verbose name is always first parameter.
          min_width: minimal image width (in pixels).
          min_height: minimal image height (in pixels).
          max_width: maximum image width (in pixels).
          max_height: maximum image height (in pixels).
          max_size: maximum image file size (in kilobytes).
        """
        super(ImageProperty, self).__init__(verbose_name, **kwds)
        self.min_width  = min_width
        self.min_height = min_height
        self.max_width  = max_width
        self.max_height = max_height
        self.max_size   = max_size

    def validate(self, value):
        from google.appengine.api import images
        """Validate image property.
    
        Returns:
          A valid value.
    
        Raises:
          BadValueError if property is image incorrect size.
        """
        value = super(ImageProperty, self).validate(value)
        # value not defined
        if value is None:
            return value
        # check image size
        if self.min_width or self.min_height or self.max_width or self.max_height:
            image = images.Image(value)
            if (self.min_width is not None and image.width < self.min_width) or \
               (self.min_height is not None and image.height < self.min_height):
                raise BadValueError('Property %s has too small width or height' % self.name)
            if (self.max_width is not None and image.width > self.max_width) or \
               (self.max_height is not None and image.height > self.max_height):
                raise BadValueError('Property %s has too large width or height' % self.name)
        # check image file size
        if self.max_size and len(value) > self.max_size * 1024:
            raise BadValueError('Property %s has too large content' % self.name)
        return value

class UserProperty(Property):
    """A user property."""

    def __init__(self,
                 auto_current_user=False,
                 auto_current_user_add=False,
                 **kwargs):
        """Initializes this Property with the given options.
    
        Note: this does *not* support the 'default' keyword argument.
        Use auto_current_user_add=True instead.
    
        Args:
          verbose_name: User friendly name of property.
          name: Storage name for property.  By default, uses attribute name
            as it is assigned in the Model sub-class.
          required: Whether property is required.
          validator: User provided method used for validation.
          choices: User provided set of valid property values.
          auto_current_user: If true, the value is set to the current user
            each time the entity is written to the datastore.
          auto_current_user_add: If true, the value is set to the current user
            the first time the entity is written to the datastore.
          indexed: Whether property is indexed.
        """
        from apps.user.models import User
        super(UserProperty, self).__init__(**kwargs)
        self.auto_current_user = auto_current_user
        self.auto_current_user_add = auto_current_user_add
        self.data_type = User

    def validate(self, value):
        """Validate user.
    
        Returns:
          A valid value.
    
        Raises:
          BadValueError if property is not instance of 'User'.
        """
        value = super(UserProperty, self).validate(value)
        if value is not None and not isinstance(value, self.data_type):
            raise BadValueError('Property %s must be a %s' % (self.name, self.data_type.__class__.__name__))
        return value

    def default_value(self):
        """Default value for user.
    
        Returns:
          Value of get_current_user() if auto_current_user or
          auto_current_user_add is set; else None. (But *not* the default
          implementation, since we don't support the 'default' keyword
          argument.)
        """
        from apps.user import get_current_user
        if self.auto_current_user or self.auto_current_user_add:
            return get_current_user()
        return None

    def get_value_for_datastore(self, model_instance):
        """Get value from property to send to datastore.
    
        Returns:
          Value of get_current_user() if auto_current_user is set;
          else the default implementation.
        """
        user = None
        from apps.user import get_current_user
        if self.auto_current_user:
            user = get_current_user()
        else:
            user = super(UserProperty, self).get_value_for_datastore(model_instance)
        # return user representation for save as Key
        return user and user.key()

    def make_value_from_datastore(self, value):
        if value is None:
            return None
        # restore user object by key
        return self.data_type.get(value)

class StringProperty(StringProperty):
    """A textual property, which can be multi- or single-line."""

    def __init__(self, verbose_name=None, multiline=False, min_length=None, max_length=None, **kwds):
        """Construct string property.
        
        Args:
            verbose_name: Verbose name is always first parameter.
            multi-line: Carriage returns permitted in property.
            min_length: Minimal length of string.
            max_length: Maximal length of string.
        """
        super(StringProperty, self).__init__(verbose_name, **kwds)
        self.multiline = multiline
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        """Validate string property.
        
        Returns:
            A valid value.
        
        Raises:
            BadValueError if property is not multi-line but value is.
        """
        value = super(StringProperty, self).validate(value)
        if self.min_length and len(value) < self.min_length:
            raise BadValueError('Value is too short')
        if self.max_length and len(value) > self.max_length:
            raise BadValueError('Value is too long')
        return value

class SlugProperty(StringProperty):
    '''String starts with letter and contain only characters, numbers, underscores, dots and minus signs'''

    def validate(self, value):
        value = super(SlugProperty, self).validate(value)
        value = value.lower()
        if not re.match("^[\w._-]+$", value, flags=re.UNICODE):
            raise BadValueError('Value %r should contain only letters, numbers, dots, underscore and minus sign' % self.name)
        return value