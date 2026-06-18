from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.NoteListView.as_view(), name='list'),
    path('new/', views.NoteCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.NoteUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.NoteDeleteView.as_view(), name='delete'),
    path('detail/<int:pk>/', views.NoteDetailView.as_view(), name='detail'),
    path('public/', views.PublicFeedView.as_view(), name='public_feed'),
    path('comment/<int:pk>/', views.add_comment, name='add_comment'),
    path('like/<int:pk>/', views.toggle_like, name='toggle_like')

]