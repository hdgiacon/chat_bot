from django.urls import path
from .views import UserCreateView, UserListView, UserReadView, UserUpdateView, UserDeleteView

app_name = 'user'

urlpatterns = [
    path('list/users/', UserListView.as_view(), name = 'user-list'),
    path('create/', UserCreateView.as_view(), name = 'user-create'),
    path('<int:pk>/', UserReadView.as_view(), name = 'user-read'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name = 'user-update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name = 'user-delete'),
]