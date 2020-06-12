from django.urls import path
from . import views

app_name = 'reference'
urlpatterns = [
    #path('', views.post_list, name='post_list'),
    #path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('', views.ReferenceListView.as_view(), name='reference_list'),
    #path('', views.PostListView.as_view(('reference.urls', 'post_list'), namespace='post_list')),
    #path('tag/<slug:tag_slug>/', views.PostListView, name='post_list_by_tag'),
    #path('<int:year>/<int:month>/<int:day>/<slug:post>', views.post_detail, name='post_detail'),
    #path('post/<int:pk>-<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    #path('<int:post_id>/share/', views.post_share, name='post_share'),
    #path('feed/', LatestPostsFeed(), name='post_feed'),
    #path('search/', views.post_search, name='post_search'),
    path('reference/add/', views.ReferenceCreateView.as_view(), name='reference_create'),
    path('reference/<int:pk>-<slug:slug>/update/', views.ReferenceUpdateView.as_view(), name='reference_update'),
    path('reference/<int:pk>-<slug:slug>/delete/', views.ReferenceDeleteView.as_view(), name='reference_delete'),
    
]