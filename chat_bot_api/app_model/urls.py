from django.urls import path
from .views import SendDatabaseAndTrainModel, TrainTaskStatusView, SearchInformationView

urlpatterns = [
    path('train/model/', SendDatabaseAndTrainModel.as_view(), name = 'send-database'),
    path('monitor/training/', TrainTaskStatusView.as_view(), name = 'task-status'),
    path('search/information/', SearchInformationView.as_view(), name = 'search-information'),
]