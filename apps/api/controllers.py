'''
API - allow you to create API methods to access
to your site from external places.
''' 

def run_api_method(request, app_name, action, **params):
    module = __import__("%s.api" % app_name, fromlist=["api"])
    func = getattr(module, action)
    return func(request, **params)
