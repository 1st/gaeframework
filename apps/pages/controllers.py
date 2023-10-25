from django.template import TemplateDoesNotExist

def render(request, template):
    try:
        return request.render("pages/%s" % template)
    except TemplateDoesNotExist, err:
        raise request.PAGE_NOT_FOUND(err)