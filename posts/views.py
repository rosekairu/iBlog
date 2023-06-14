from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Author, Post, Category
from marketing.models import Signup
from .forms import CommentForm


def get_author(user):
    if user is not None and user.is_active:
        return Author.objects.get(user=user)
    return None


def home(request):
    recent = Post.objects.latest('date')
    author = get_author(request.user)    

    context = {
        'recent': recent,
        'author': author,
        'profile_picture': author.profile_picture if author else None,
        'description': author.description if author else None,
    }
    return render(request, 'home.html', context)


def blog(request):
    category_count = get_category_count()
    post_list = Post.objects.all()
    recent = Post.objects.order_by('-date')[0:3]
    author = get_author(request.user)

    if request.method == "POST":
        email = request.POST["email"]
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()

    paginator = Paginator(post_list, 3)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'page_request_var': page_request_var,
        'recent': recent,
        'category_count': category_count,
        'author': author,
        'profile_picture': author.profile_picture if author else None,
        'description': author.description if author else None,
    }

    return render(request, 'blog.html', context)

def post(request, id):
    post = get_object_or_404(Post, id=id)
    category_count = get_category_count()
    featured = Post.objects.filter(featured=True)
    recent = Post.objects.order_by('-date')[0:3]
    author = get_author(request.user)
    form = CommentForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            if request.user.is_authenticated:
                form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': post.id
            }))
        
    context = {
        'form': form, 
        'post': post,
        'object_list': featured,
        'recent': recent,
        'category_count': category_count,
        'author': author,
        'profile_picture': author.profile_picture if author else None,
        'description': author.description if author else None,
    }
    return render(request, 'post.html', context)

def category(request):
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})


def get_category_count():
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title'))
    return queryset


# def post_create(request):
#     title = 'Create'
#     form = PostForm(request.POST or None, request.FILES or None)
#     if request.method == "POST":
#         print('POST request received')
#         print('Form data:', request.POST)
#         if form.is_valid():
#             print(form.errors)
#             form.save()
#             return redirect(reverse("post", kwargs={'id': form.instance.id}))

#     context = {
#         'title': title,
#         'form': form
#     }
#     return render(request, "post_create.html", context)
