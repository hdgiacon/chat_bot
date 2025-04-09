from django.urls import path
from .views import CustomTokenObtainPairView, LogoutView, CustomTokenRefreshView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name = 'auth_logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name = 'token_refresh'),
]