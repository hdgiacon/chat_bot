from django.urls import path
from .views import UserCreate, UserList, UserRead, UserUpdate, UserDelete

urlpatterns = [
    path('list/users/', UserList.as_view(), name = 'user-list'),
    path('create/', UserCreate.as_view(), name = 'user-create'),
    path('<int:pk>/', UserRead.as_view(), name = 'user-read'),
    path('<int:pk>/update/', UserUpdate.as_view(), name = 'user-update'),
    path('<int:pk>/delete/', UserDelete.as_view(), name = 'user-delete'),
]