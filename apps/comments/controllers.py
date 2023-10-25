'''
Comments - attach comments to any object.
'''
import re
from gae import db
from apps.comments.forms import UserCommentForm
from apps.user import login_required

@login_required()
def create_comment(request):
    """
    Create a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comment/preview.html``, will be rendered.
    """
    data = request.POST.copy()
    if data:
        # get object model name
        object_key = db.Key(data['obj'])
        object_type = object_key.kind()
        # get application name
        path = re.findall("[A-Z][^A-Z]*", object_type)[0].lower()
        try:
            # load module with object, attached to comment
            __import__("%s.models" % (path))
        except ImportError:
            raise Exception("Not found object '%s' in application '%s'" % (object_type, path))
        # filled form
        form = UserCommentForm(data=data, initial={"obj": object_key})
        # preview the comment
        if "preview" in data or not form.is_valid():
            return request.render(
                'comments/preview',
                form = form,
                comment = form.data.get("text", ""),
            )
        form.save()
    return request.redirect("go back")
