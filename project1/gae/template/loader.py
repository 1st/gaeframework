"""
Wrapper for loading templates from apps "templates" directories.
"""

import os, sys, logging
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
from django.utils._os import safe_join
from gae.tools import installed_apps

# At compile time, cache the directories to search.
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_template_dirs = {}
for app in installed_apps():
    template_dir = os.path.join('apps', app, 'templates')
    if os.path.isdir(template_dir):
        app_template_dirs[app] = template_dir.decode(fs_encoding)


class Loader(BaseLoader):
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs". Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """
        if not template_dirs:
            template_dirs = app_template_dirs
        try:
            app_name, template_path = template_name.split("/", 1)
        except ValueError:
            raise TemplateDoesNotExist, "Not specified application prefix in '%s' template path" % template_name
        if "site" in template_dirs: # global template
            yield safe_join(template_dirs.get("site"), template_name)
        if template_dirs.get(app_name) is not None: # template in application
            yield safe_join(template_dirs.get(app_name), template_path)

    def load_template_source(self, template_name, template_dirs=None):
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                file = open(filepath)
                try:
                    return (file.read().decode(settings.FILE_CHARSET), filepath)
                finally:
                    file.close()
            except IOError:
                pass
        msg = "Template '%s' does not exists" % template_name
        logging.warn(msg)
        raise TemplateDoesNotExist(msg)

_loader = Loader()