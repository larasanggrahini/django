from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import (SearchVector, SearchQuery, SearchRank)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin #buat cek udah login apa belum
from django.views.generic import ListView, FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.text import slugify

# Create your views here.
@login_required
def post_list(request, tag_slug=None):

    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in =[tag])

    paginator = Paginator(object_list, 2)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'posts': posts, 'page': page, 'tag': tag})

class PostListView(LoginRequiredMixin, ListView):
    #sebenernya postlistview udah tampil, tp butuh overide biar gk cuma listnya aja yg tampil
    queryset = Post.published.all() #atribut list view, data view apa
    context_object_name = 'posts' #dari nama template list makanya posts
    paginate_by = 2
    template_name = 'blog/post/list.html'
    #overide superclass si tag_slug
    def get_queryset(self):
        qs = super().get_queryset()
        tag_slug = self.kwargs.get('tag_slug') #ambil dari urls/py body

        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            qs = qs.filter(tags__in =[tag])
            self.tag = tag #self pointer ke instance
        else:
            self.tag = None #variabel ada saat sign suatu value

        return qs

    def get_context_data(self, **kwargs): #** kwargs argument bentuk dictionary merujuk line 35 posts
        context = super().get_context_data(**kwargs)

        if self.tag:
            context['tag'] = self.tag

        return context
        #yg render si super class makanya gk ada render di sini

@login_required
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', 
                                publish__year=year, publish__month=month, publish__day=day)

    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True) #id dari tags
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id) #dapetin semua similar post kecuali dirinya sendiri
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4] #tambah field yg digenerate di setiap records, descending ambil 4 teratas


    return render(request, 'blog/post/detail.html',
                     {'post': post, 
                     'comments': comments, 
                     'new_comment': new_comment, 
                     'comment_form': comment_form,
                     'similar_posts': similar_posts})

class PostDetailView(LoginRequiredMixin, FormView):
    form_class = CommentForm
    template_name = 'blog/post/detail.html'

    def get_initial(self): #initial detail template
        pk = self.kwargs.get('pk')
        slug = self.kwargs.get('slug') #untuk security maka ditambah slug
        self.post = get_object_or_404(Post, pk=pk, slug=slug)

        self.comments = self.post.comments.filter(active=True)
        self.new_comment = None

        post_tags_ids = self.post.tags.values_list('id', flat=True) #id dari tags
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=self.post.id) #dapetin semua similar post kecuali dirinya sendiri
        self.similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4] #tambah field yg digenerate di setiap records, descending ambil 4 teratas

        return super().get_initial()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post
        context['comments'] = self.comments
        context['similar_posts'] = self.similar_posts
        return context

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.post = self.post
        new_comment.save()
        context = self.get_context_data()
        context['new_comment'] = new_comment
        
        return render(self.request, self.template_name, context=context)


@login_required
def post_share(request, post_id):
    post = get_object_or_404(Post,id=post_id,status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you to read {post.title}" #format satu variabel
            message = (f"Read {post.title} at {post_url}\n\n"
                        f"{cd['name']} comments: {cd['comments']}") #kurung() untuk string panjang, kalau satu line tidak perlu
            send_mail(subject, message, 'colors.stff@gmail.com', [cd['to'],])
            sent = True
    else: 
        form = EmailPostForm()

    return render(request, 'blog/post/share.html',
                            {'post': post, 'form': form, 'sent': sent})

@login_required
def post_search(request):
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            #results = Post.published.annotate(search = SearchVector('title', 'body')).filter(search=query) #search vector: bisa search from multiple fields
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                        search=search_vector, rank=SearchRank(
                        search_vector, search_query)).filter(search=search_query).order_by('-rank')
    else:
        form = SearchForm()
        query = None
        results = []
    
    return render(request, 'blog/post/search.html', 
                            {'form': form, 'query': query, 'results': results})

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields =['title', 'body', 'tags']
    template_name = 'blog/post/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'published'
        form.instance.slug = slugify(form.instance.title, allow_unicode=True)
        #ambil form instance, balikin ke super form_valid krn di super ada form save, jd datanya udah ditambah
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'body', 'tags']
    template_name = 'blog/post/post_form.html'
    query_pk_and_slug = True

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(author = self.request.user)

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.title, allow_unicode=True)

        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')
    query_pk_and_slug = True

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author = self.request.user)