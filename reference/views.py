from django.shortcuts import render, get_object_or_404
from .models import Reference
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.text import slugify

# Create your views here.
@login_required
def reference_list(request, tag_slug=None):

    object_list = Reference.published.all()

    paginator = Paginator(object_list, 2)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'reference/post/list.html', {'posts': posts, 'page': page})

class ReferenceListView(LoginRequiredMixin, ListView):
    #sebenernya postlistview udah tampil, tp butuh overide biar gk cuma listnya aja yg tampil
    queryset = Reference.objects.all() #atribut list view, data view apa
    context_object_name = 'posts' #dari nama template list makanya posts
    paginate_by = 2
    template_name = 'reference/post/list.html'
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

class ReferenceCreateView(LoginRequiredMixin, CreateView):
    model = Reference
    fields =['title', 'description', 'link']
    template_name = 'reference/post/reference_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        #form.instance.status = 'published'
        form.instance.slug = slugify(form.instance.title, allow_unicode=True)
        #ambil form instance, balikin ke super form_valid krn di super ada form save, jd datanya udah ditambah
        return super().form_valid(form)

class ReferenceUpdateView(LoginRequiredMixin, UpdateView):
    model = Reference
    fields = ['title', 'description', 'link']
    template_name = 'reference/post/reference_form.html'
    query_pk_and_slug = True

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(author = self.request.user)

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.title, allow_unicode=True)

        return super().form_valid(form)

class ReferenceDeleteView(LoginRequiredMixin, DeleteView):
    model = Reference
    template_name = 'reference/post/reference_confirm_delete.html'
    success_url = reverse_lazy('reference:reference_list')
    query_pk_and_slug = True

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author = self.request.user)