from gae.config import get_config
from gae import db

def index(request):
    '''
    Site home page
    '''
    return request.render("site/index")

def cron(request):
    '''
    Execute cron jobs for each application with file cron.py
    '''
    for app_name in request.installed_apps:
        cron = __import__("apps.%s.cron" % app_name)
        cron.run()
    return "Cron jobs completed!"

def data_migration(request):
    '''
    Run data migration for specified apps.
    '''
    # TODO: this handler is not completed!
    apps = request.get('apps') or request.installed_apps
    for app_name in apps:
        app_models = __import__("apps.%s.models" % app_name)
        app_models = [model for model in dir(app_models)
                      if not model.startswith('_') and model[0].isuper() and isinstance(model, db.Model)]
        for model in app_models:
            migrate_object(app_name, model)
    return "Data migration started!"

def migrate_object(request, app, model_name, key=None):
    '''
    Migrate only one model object.
    '''
    # TODO: this handler is not completed!
    current_app_version = get_config("%s.version" % app, '1.0')
    app_migrations = get_config("%s.migration" % app, [])
    app_models = __import__("apps.%s.models" % app)
    model = getattr(app_models, model_name)
    query = model.order('__key__')
    if key:
        query.filter('__key__ >', key)
    obj = query.get(key)
    if obj.version != current_app_version:
        for version in app_migrations:
            if version > obj.version and model_name in version.keys():
                changed_fields = version[model_name]
    return "Object migrated!"

def warmup(request):
    '''
    Pre-load code before real request to be executed.
    '''
    return "Warmup was load all required data"
