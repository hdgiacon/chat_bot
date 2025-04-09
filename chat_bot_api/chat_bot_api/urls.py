from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
   path('admin/', admin.site.urls),
   path(
      '', 
      TemplateView.as_view(
         template_name = 'core/swagger-ui.html',
         extra_context = {'schema_url': 'openapi-schema'}
      ),    
      name = 'documentation'
   ),
   path('app_auth/', include('app_auth.urls')),
   path('user/', include('user.urls'))
]
