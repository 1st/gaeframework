'''
Blogs - multiple blogs in one application
''' 
#from gae.tools.pagination import Pagination
#from gae.shortcuts import get_object_or_404
#from apps.user import login_required
#from apps.blog.models import Entity
#from apps.blog.forms import EntityCreateForm, EntityEditForm
from google.appengine.api.images import get_serving_url
from apps.images.tools import save_image

def upload_image(request):
    # TODO: check user access level
    # TODO: change image size
    if not (request.files and request.files.has_key('image')):
        raise request.NOT_FOUND
    data = request.files['image'].stream.read()
    blob_key = save_image(data)
    return request.json(
        blob_key = blob_key,
        image_url = get_serving_url(blob_key),
    )

def show_image(request, blob_key):
    company = Company.get_by_identifier(identifier)
    if not (company and company.logo_url):
        raise request.NOT_FOUND
    return redirect(company.logo_url)
