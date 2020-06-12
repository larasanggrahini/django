from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse_lazy

# Create your models here.
class GetReferenceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

class Reference(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish', blank=True)
    description = models.TextField()
    link = models.URLField(max_length=250)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    #on_delete=models.CASCADE, related_name = 'blog_posts')created = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publish = models.DateTimeField(default=timezone.now)

    objects = models.Manager()
    getReference = GetReferenceManager()

    class Meta:
        #ordering = ('created',)
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('reference:reference_list')
