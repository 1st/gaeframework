'''
Test application.
'''
from apps.guestbook.models import Message
from apps.guestbook.forms import MessageForm

def items_list(request, on_page=10, page=1, template=None):
    greetings = Message.all().order('-date').fetch(on_page)
    return request.render(template or 'guestbook/items_list', greetings = greetings)

def create_item(request):
    if request.POST:
        # filled form
        form = MessageForm(data=request.POST)
        if form.is_valid():
            form.save()
            request.redirect(request.previous_page)
    else:
        # empty form
        form = MessageForm()
    # show form with specified data
    return request.render('guestbook/create_item', form = form)
