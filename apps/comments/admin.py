'''
Administration interface.
'''
from apps.comments.forms import CommentAdminForm, CommentInlineAdminForm

class Comment():
    name = "Comments list"
    forms = (CommentAdminForm, # create
             CommentAdminForm, # edit
             CommentInlineAdminForm) # edit multiple records