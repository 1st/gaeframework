'''
Blogs - multiple blogs in one application
''' 
from gae.shortcuts import get_object_or_404
from gae.tools.pagination import Pagination
from apps.user import login_required
from apps.blogs.models import Blog, Entity
from apps.blogs.forms import BlogCreateForm, BlogEditForm,\
                             EntityCreateForm, EntityEditForm

''' operations with blogs '''

def blogs_list(request):
    blogs = Blog.all().order('-created')
    # show not published blogs
    if request.GET.get("show") == "unpublished" and request.user:
        # show all blogs
        blogs.filter('active', False)
        # show only user blogs
        if not request.user.is_admin:
            blogs.filter('author', request.user)
    # show only active blogs
    else:
        blogs.filter('active', True)
    # render page
    return request.render(
        'blog/blogs_list',
        blogs = Pagination(request, blogs, 20, "blogs_page"),
    )

@login_required()
def blog_create(request):
    if request.POST:
        form = BlogCreateForm(data=request.POST)
        # filled form
        if form.is_valid():
            form.save()
            return request.redirect("go back")
    else:
        # empty form
        form = BlogCreateForm()
    # render page
    return request.render('blog/blog_create', form = form)

@login_required()
def blog_edit(request, blog):
    blog_obj = Blog.get_by_key_name(blog)
    # item not found
    if blog_obj is None:
        raise request.PAGE_NOT_FOUND
    if request.POST:
        # filled form
        form = BlogEditForm(data=request.POST, instance=blog_obj)
        if form.is_valid():
            form.save()
            return request.redirect("go back")
    else:
        # empty form with initial data
        form = BlogEditForm(instance=blog_obj)
    # render page
    return request.render('blog/blog_edit', form = form)

@login_required()
def blog_delete(request, blog):
    blog_obj = Blog.get_by_key_name(blog)
    # item not found
    if blog_obj is None:
        raise request.PAGE_NOT_FOUND
    # delete blog
    blog_obj.delete()
    return request.redirect("go back")

''' operations with blog entities '''

def entities_list(request, blog=None, tags=None):
    blog_obj = blog and Blog.get_by_key_name(blog)
    entities = Entity.all().order('-changed')
    if blog_obj:
        entities.filter('blog', blog_obj)
    if tags:
        entities.filter('tags IN', tags.strip().split(','))
    # show not published entities
    if request.GET.get("show") == "unpublished" and request.user:
        # show all entities
        entities.filter('active', False)
        # show only user entities
        if not request.user.is_admin:
            entities.filter('author', request.user)
    # show only active blogs
    else:
        entities.filter('active', True)
    # render page
    return request.render(
        'blog/entities_list',
        blog = blog_obj,
        entities = Pagination(request, entities, 20, "entities_page"),
    )

def entity_details(request, blog, entity):
    blog_obj = get_object_or_404(Blog, slug=blog)
    entity_obj = get_object_or_404(Entity, slug="%s/%s" % (blog_obj.key().name(), entity))
    # render page
    return request.render(
        'blog/entity_details',
        blog = blog_obj,
        entity = entity_obj,
    )

@login_required()
def entity_create(request, blog):
    blog_obj = get_object_or_404(Blog, slug=blog)
    if request.POST:
        form = EntityCreateForm(data=request.POST, initial={'blog': blog_obj})
        # filled form
        if form.is_valid():
            form.save()
            return request.redirect("go back")
    else:
        # empty form
        form = EntityCreateForm()
    # render page
    return request.render('blog/entity_create', form = form)

@login_required()
def entity_edit(request, blog, entity):
    blog_obj = get_object_or_404(Blog, slug=blog)
    entity_obj = get_object_or_404(Entity, slug="%s/%s" % (blog_obj.key().name(), entity))
    if request.POST:
        # filled form
        form = EntityEditForm(data=request.POST, instance=entity_obj)
        if form.is_valid():
            form.save()
            return request.redirect("go back")
    else:
        # empty form with initial data
        form = EntityEditForm(instance=entity_obj)
    # render page
    return request.render('blog/entity_edit', form = form)

@login_required()
def entity_delete(request, blog, entity):
    blog_obj = get_object_or_404(Blog, slug=blog)
    entity_obj = get_object_or_404(Entity, slug="%s/%s" % (blog_obj.key().name(), entity))
    # delete blog entity
    entity_obj.delete()
    return request.redirect("go back")