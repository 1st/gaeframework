'''
Administration interface.
'''
from apps.guestbook.forms import MessageAdminForm, MessageInlineAdminForm

class Message():
    name = "Guestbook messages list"
    forms = (MessageAdminForm, # create
             MessageAdminForm, # edit
             MessageInlineAdminForm) # edit multiple records
