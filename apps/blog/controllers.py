'''
Blogs - multiple blogs in one application
''' 
from gae.tools.pagination import Pagination
from gae.shortcuts import get_object_or_404
from apps.user import login_required
from apps.blog.models import Entity
from apps.blog.forms import EntityCreateForm, EntityEditForm

def entries_list(request, tags=None):
    entries = Entity.all().order('-changed')
    if tags:
        entries.filter('tags IN', tags.strip().split(','))
    # show not published entries
    if request.GET.get("show") == "unpublished" and request.user:
        # show all entries
        entries.filter('active', False)
        # show only user entries
        if not request.user.is_admin:
            entries.filter('author', request.user)
    # show only active entries
    else:
        entries.filter('active', True)
    # render page
    return request.render(
        'blog/entries_list',
        entries = Pagination(request, entries, 10, "entries_page"),
    )

def entry_details(request, entry):
    entry_obj = get_object_or_404(Entity, slug=entry)
    return request.render('blog/entry_details', entry = entry_obj)

@login_required()
def create_entry(request):
    if request.POST:
        form = EntityCreateForm(data=request.POST)
        # filled form
        if form.is_valid():
            form.save()
            return request.redirect("go back")
    else:
        # empty form
        form = EntityCreateForm()
    # render page
    return request.render('blog/create_entry', form = form)

@login_required()
def edit_entry(request, entry):
    entry_obj = get_object_or_404(Entity, slug=entry)
    if request.POST:
        # filled form
        form = EntityEditForm(data=request.POST, instance=entry_obj)
        if form.is_valid():
            form.save()
            return request.redirect("go back")
    else:
        # empty form with initial data
        tags = ", ".join(entry_obj.tags or [])
        form = EntityEditForm(instance=entry_obj, initial={"tags": tags})
    # render page
    return request.render('blog/edit_entry', form = form)

@login_required()
def delete_entry(request, entry):
    entry_obj = get_object_or_404(Entity, slug=entry)
    entry_obj.delete()
    return request.redirect("go back")