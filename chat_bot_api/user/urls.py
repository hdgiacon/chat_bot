from django.urls import path
from .views import UserCreateView, UserListView, UserReadView, UserUpdateView, UserDeleteView

app_name = 'user'

urlpatterns = [
    path('list/users/', UserListView.as_view(), name = 'user-list'),
    path('create/', UserCreateView.as_view(), name = 'user-create'),
    path('read/', UserReadView.as_view(), name = 'user-read'),
    path('update/', UserUpdateView.as_view(), name = 'user-update'),
    path('delete/', UserDeleteView.as_view(), name = 'user-delete'),
]