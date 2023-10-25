from django.utils import simplejson
from apps.location.models import City
#from apps.user import login_required

def cities_list(request):
    '''Return cities list'''
    cities = City.all().order("name").count(10)
    # show only cities with specified prefix
    search_by_prefix = request.get("prefix")
    if search_by_prefix:
        cities.filter("name>=", search_by_prefix).filter("name<", search_by_prefix + u"\ufffd")
    # ajax request
    if request.is_xhr:
        request.response.headers.add_header("Content-Type", 'application/json')
        return simplejson.dumps(cities or [])
    return request.render('location/cities_list', cities = cities)