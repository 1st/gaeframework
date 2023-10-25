'''
Todo - list of actual tasks.
'''
from google.appengine.api import mail
from apps.user import login_required
from apps.todo.models import Todo
from apps.todo.forms import TodoForm

def todo_list(request, on_page=10, page=1, finished=False):
    todos = Todo.gql("WHERE author = :1 and finished = :2",
                     request.user, finished)
    return request.render(
        'todo/todo_list',
        todos = todos,
        todos_pages = todos.count(),
    )

def todo_details(request):
    pass

@login_required()
def create_task(request):
    if request.POST:
        # filled form
        form = TodoForm(data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task.save()
            return request.redirect("go back")
    else:
        # empty form
        form = TodoForm()
    # render page
    return request.render('todo/create_task', form = form)

@login_required()
def edit_todo(request):
    raise request.PAGE_NOT_FOUND

@login_required()
def delete_todo(request, todo_id):
    todo_id = int(todo_id)
    todo = Todo.get_by_id(todo_id)
    todo.delete()
    return request.redirect("go back")

@login_required()
def send_mail(request, todo_id):
    todo_id = int(todo_id)
    todo = Todo.get_by_id(todo_id)
    message = mail.EmailMessage(sender  = request.user.email,
                                subject = todo.shortDescription)
    message.to = request.user.email
    message.body = todo.longDescription
    message.send()
    request.redirect('go back')