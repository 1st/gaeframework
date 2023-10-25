#!/usr/bin/python
'''
Manage GAE framework projects.
'''
import os, sys, fileinput, code, getpass, urllib2, gae
from shutil import copyfile, copytree
gae_dir = os.path.dirname(gae.__file__)
appengine_dir = os.path.join(os.path.dirname(gae_dir), 'google_appengine')
EXTRA_PATHS = [
  appengine_dir,
  os.path.join(appengine_dir, 'lib', 'antlr3'),
  os.path.join(appengine_dir, 'lib', 'fancy_urllib'),
  os.path.join(appengine_dir, 'lib', 'ipaddr'),
  os.path.join(appengine_dir, 'lib', 'protorpc'),
  os.path.join(appengine_dir, 'lib', 'webob'),
  os.path.join(appengine_dir, 'lib', 'yaml', 'lib'),
  os.path.join(appengine_dir, 'lib', 'simplejson'),
  os.path.join(appengine_dir, 'lib', 'graphy'),
]
sys.path = EXTRA_PATHS + sys.path
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db
import yaml

LOCAL_HOST = '127.0.0.1:8000'


def usage(app_name):
    return """
Usage: %s <command>

Commands:
  run [project]             Run development server.
  deploy [project]          Deploy project to server.
  debug [project]           Run project shell to debug code.
      --remote              Work with remote datastore (on server).
  new [project]             Create new project.
      --replace             Create new project in existing directory.
  new [project].[app]       Create new application in given project.
      --replace             Replace already created application.
  install [project].[app]   Create symlink to application into 'apps'.
  test [project]            Run tests for project.
  test [project].[app]      Run tests for application in given project.""" % app_name


def create_project(project_name):
    '''
    Create new project (if not exists)
    '''
    gae_destination = os.path.join(os.getcwd(), project_name, 'gae')
    project_dir_source = os.path.join(gae_dir, 'sceleton', 'project')
    project_dir_destination = os.path.join(os.getcwd(), project_name)
    # copy project directory
    if os.path.exists(project_dir_destination):
        print '%s project already exists' % project_name
        return False
    copytree(project_dir_source, project_dir_destination)
    # create symlink to gae framework directory
    os.symlink(gae_dir, gae_destination)
    # replace placeholder to project name
    replace_text(project_dir_destination, "[project_name]", project_name, recurcive=True)
    print '%s project created' % project_name
    # inslatt required applications
    install_app(project_name, 'user')
    return True


def create_app(project_name, app_name):
    '''
    Create new application (if not exists)
    '''
    app_dir_source = os.path.join(gae_dir, 'sceleton', 'app')
    app_dir_destination = os.path.join(os.getcwd(), project_name, 'apps', app_name)
    # copy application directory
    if os.path.exists(app_dir_destination):
        print '%s.%s application already exists' % (project_name, app_name)
        return False
    copytree(app_dir_source, app_dir_destination)
    # replace placeholder to application name
    replace_text(app_dir_destination, "[app_name]", app_name, recurcive=True)
    print '%s.%s application created' % (project_name, app_name)
    return True


def install_app(project_name, app_name):
    '''
    Create symlink to application located in 'apps' package (if this application not installed)
    '''
    app_dir_source = os.path.join(os.path.dirname(gae_dir), 'apps', app_name)
    app_dir_destination = os.path.join(os.getcwd(), project_name, 'apps', app_name)
    # check application in 'apps' package
    if not os.path.exists(app_dir_source):
        print '%s application not available to installation' % app_name
        return False
    # check application in the project
    if os.path.exists(app_dir_destination):
        print '%s.%s application already installed' % (project_name, app_name)
        return False
    # create symlink to application
    os.symlink(app_dir_source, app_dir_destination)
    print '%s.%s application installed' % (project_name, app_name)
    return True


def debug_project(project_name, remote=False):
    '''
    Run project shell to debug code (pass --remote to work with server datastore)
    '''
    project_dir = os.path.join(os.getcwd(), project_name)
    os.chdir(project_dir)
    try:
        config_file = os.path.join(project_dir, 'app.yaml')
        fd = open(config_file)
        config = yaml.load(fd)
        fd.close()
        app_id = config.get('application')
    except:
        raise Exception("Configuration file '%s' not found" % config_file)
    
    if remote:
        host = '%s.appspot.com' % app_id
        def auth_func():
            print "Authenticate on Google App Engine server (%s)" % host
            return raw_input('Username: '), getpass.getpass('Password: ')
        
#        remote_api_stub.ConfigureRemoteDatastore(app_id, '/_ah/remote_api', auth_func, host)
#        code.interact('App Engine interactive console for %s' % host, None, locals())
    else:
        def auth_func():
            return ("foo", "bar")
        host = LOCAL_HOST
#        code.interact('App Engine interactive console for %s' % app_id, None, locals())
    try:
        remote_api_stub.ConfigureRemoteDatastore(app_id, '/_ah/remote_api', auth_func, host)
        remote_api_stub.MaybeInvokeAuthentication()
    except urllib2.HTTPError:
        remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)
        remote_api_stub.MaybeInvokeAuthentication()
    code.interact('App Engine interactive console for %s' % host, None, locals())
    return True


def test_project(project_name):
    '''
    Run project tests
    '''
    pass


def test_app(project_name, app_name):
    '''
    Run application tests
    '''
    pass


def replace_text(path, find_me, replace_to, recurcive=False):
    '''
    Replace one text to another in all files in the given directory
    '''
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isdir(file_path) and not os.path.islink(file_path) and recurcive:
            replace_text(file_path, find_me, replace_to, recurcive)
        elif os.path.isfile(file_path):
            for line in fileinput.FileInput(file_path, inplace=1):
                line = line.replace(find_me, replace_to)
                sys.stdout.write(line)
    return True


def main(command, project_name, *args):
    '''
    Execute command
    '''
    project_name = project_name.strip(' /\\') # delete slash around project name
    sys.path.insert(0, os.path.join(os.getcwd(), project_name))
    if command == "run":
        flags = ["--address=%s" % LOCAL_HOST.split(':')[0],
                 "--port=%s" % LOCAL_HOST.split(':')[1],
                 "--datastore_path=%s/.datastore" % project_name,
                 "--history_path=%s/.history" % project_name,
                 "--blobstore_path=%s/.blobstore" % project_name,
                 "--use_sqlite",
                 "--require_indexes",
                 "--disable_static_caching",
                 ] + list(args)
        os.system(os.path.join(os.path.dirname(gae_dir),
                               'google_appengine',
                               'dev_appserver.py %s %s') % (" ".join(flags), project_name))
    elif command == "deploy":
        # compile templates (Jinja2, Closure)
        # deploy to server
        os.system(os.path.join(os.path.dirname(gae_dir), 'google_appengine', 'appcfg.py update %s') % project_name)
    elif command == "debug":
        remote = "--remote" in args
        debug_project(project_name, remote=remote)
    elif command == "new":
        try:
            project_name, app_name = project_name.split('.', 1)
            create_project(project_name)
            create_app(project_name, app_name)
        except ValueError:
            create_project(project_name)
    elif command == "install":
        try:
            project_name, app_name = project_name.split('.', 1)
            create_project(project_name)
            install_app(project_name, app_name)
        except ValueError:
            raise Exception("Please, specify application name in style 'gae-manage.py install project_name.app_name'")
    elif command == "test":
        try:
            project_name, app_name = project_name.split('.', 1)
            test_app(project_name, app_name)
        except ValueError:
            test_project(project_name)
    else:
        raise TypeError
    print ''
    print 'Command execution completed!'


if __name__ == '__main__':
    try:
        main(*sys.argv[1:])
    except TypeError:
        print usage(sys.argv[0])
